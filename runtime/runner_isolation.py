"""Fail-closed Linux namespace launcher for role-specific untrusted work."""

from __future__ import annotations

import json
import resource
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, Literal, Self

from pydantic import Field, StrictInt, StringConstraints, model_validator

from contracts.common import FrozenModel, Identifier
from policies import CapabilityProfile, load_capability_profile

MAX_RUNNER_PROFILE_BYTES = 16_000
MAX_ARGV_ITEMS = 32
MAX_ARGV_BYTES = 32_000
MAX_RUNNER_ADDRESS_SPACE_BYTES = 512 * 1024 * 1024
RUNNER_PROFILE_NAMES = (
    "analyst_v1.json",
    "pm_v1.json",
    "data_engineer_v1.json",
    "qa_v1.json",
    "reviewer_v1.json",
)

ProfileFilename = Annotated[str, StringConstraints(pattern=r"^[a-z][a-z0-9_]{0,63}\.json$")]


class RunnerIsolationError(RuntimeError):
    """A runner profile, sandbox boundary, or isolated execution failed closed."""


class RunnerProfile(FrozenModel):
    """Code-owned identity and resource envelope for one isolated role process."""

    schema_version: Literal[1] = 1
    runner_id: Identifier
    actor_id: Identifier
    role: Identifier
    namespace_uid: StrictInt = Field(ge=60_000, le=64_999)
    capability_profile: ProfileFilename | None
    max_input_bytes: StrictInt = Field(ge=1, le=2_000_000)
    max_output_bytes: StrictInt = Field(ge=1, le=2_000_000)
    timeout_seconds: StrictInt = Field(ge=1, le=1_200)

    @model_validator(mode="after")
    def validate_role_shape(self) -> Self:
        if self.role == "pm" and self.capability_profile is not None:
            raise ValueError("PM runner must not have a capability profile")
        if self.role != "pm" and self.capability_profile is None:
            raise ValueError("tool-using runner requires a capability profile")
        return self


class LoadedRunnerProfile(FrozenModel):
    runner: RunnerProfile
    capability: CapabilityProfile | None = None


class RunnerResult(FrozenModel):
    runner_id: Identifier
    actor_id: Identifier
    namespace_uid: StrictInt
    payload: dict[str, Any]


def _bounded_regular_file(path: Path, *, limit: int, label: str) -> bytes:
    if path.is_symlink():
        raise RunnerIsolationError(f"{label} must not be a symlink")
    try:
        before = path.stat()
        payload = path.read_bytes()
        after = path.stat()
    except OSError as error:
        raise RunnerIsolationError(f"{label} cannot be read: {type(error).__name__}") from None
    before_id = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    after_id = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
        raise RunnerIsolationError(f"{label} must be a bounded regular file")
    if before_id != after_id or len(payload) != before.st_size:
        raise RunnerIsolationError(f"{label} changed while reading")
    return payload


def load_runner_profile(repository_root: Path, name: str) -> LoadedRunnerProfile:
    """Load one strict runner profile and bind it to the matching capability profile."""

    if name not in RUNNER_PROFILE_NAMES:
        raise RunnerIsolationError("runner profile name is not allowlisted")
    root = repository_root.resolve(strict=True)
    if repository_root.is_symlink() or not root.is_dir():
        raise RunnerIsolationError("repository root must be a real directory")
    path = root / "policies/runner_profiles" / name
    current = root
    for part in path.relative_to(root).parts:
        current /= part
        if current.is_symlink():
            raise RunnerIsolationError("runner profile path contains a symlink")
    payload = _bounded_regular_file(path, limit=MAX_RUNNER_PROFILE_BYTES, label="runner profile")
    try:
        runner = RunnerProfile.model_validate_json(payload, strict=True)
    except ValueError as error:
        raise RunnerIsolationError("runner profile is not valid version-one JSON") from error
    capability = None
    if runner.capability_profile is not None:
        capability_path = root / "policies/profiles" / runner.capability_profile
        try:
            capability = load_capability_profile(capability_path)
        except ValueError as error:
            raise RunnerIsolationError(str(error)) from None
        if capability.role != runner.role:
            raise RunnerIsolationError("runner role does not match its capability profile")
    return LoadedRunnerProfile(runner=runner, capability=capability)


def load_all_runner_profiles(repository_root: Path) -> tuple[LoadedRunnerProfile, ...]:
    profiles = tuple(load_runner_profile(repository_root, name) for name in RUNNER_PROFILE_NAMES)
    runners = [item.runner for item in profiles]
    for field in ("runner_id", "actor_id", "namespace_uid"):
        values = [getattr(item, field) for item in runners]
        if len(values) != len(set(values)):
            raise RunnerIsolationError(f"runner {field} values must be unique")
    return profiles


def _safe_workspace(repository: Path, workspace_path: Path) -> Path:
    expected_parent = repository / ".scenario-state/workspaces"
    lexical = workspace_path.absolute()
    try:
        relative = lexical.relative_to(expected_parent)
    except ValueError:
        raise RunnerIsolationError("runner workspace escaped managed scenario workspaces") from None
    current = expected_parent
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise RunnerIsolationError("runner workspace path contains a symlink")
    try:
        workspace = workspace_path.resolve(strict=True)
    except OSError as error:
        raise RunnerIsolationError(
            f"runner workspace cannot be resolved: {type(error).__name__}"
        ) from None
    if not workspace.is_dir() or not workspace.is_relative_to(expected_parent):
        raise RunnerIsolationError("runner workspace escaped managed scenario workspaces")
    return workspace


def _wildcard_root(pattern: str) -> PurePosixPath:
    parts = PurePosixPath(pattern).parts
    fixed: list[str] = []
    for part in parts:
        if "*" in part:
            break
        fixed.append(part)
    if not fixed:
        raise RunnerIsolationError("runner write pattern has no fixed directory root")
    return PurePosixPath(*fixed)


def _safe_match(workspace: Path, candidate: Path) -> Path:
    try:
        lexical_relative = candidate.absolute().relative_to(workspace)
    except ValueError:
        raise RunnerIsolationError("runner readable path escaped workspace") from None
    current = workspace
    for part in lexical_relative.parts:
        current /= part
        if current.is_symlink():
            raise RunnerIsolationError("runner readable path contains a symlink")
    if not candidate.is_file():
        raise RunnerIsolationError("runner readable path must be a regular non-symlink file")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_relative_to(workspace):
        raise RunnerIsolationError("runner readable path escaped workspace")
    return resolved


class IsolatedRunner:
    """Execute trusted argv with untrusted JSON inside a role-specific bwrap sandbox."""

    def __init__(
        self,
        repository_root: Path,
        profile: LoadedRunnerProfile,
        workspace_path: Path | None,
    ) -> None:
        if repository_root.is_symlink():
            raise RunnerIsolationError("repository root must not be a symlink")
        self.repository = repository_root.resolve(strict=True)
        self.profile = profile
        if profile.runner.role == "pm":
            if workspace_path is not None:
                raise RunnerIsolationError("PM runner must not receive a workspace")
            self.workspace = None
        else:
            if workspace_path is None:
                raise RunnerIsolationError("tool-using runner requires a workspace")
            self.workspace = _safe_workspace(self.repository, workspace_path)
        if shutil.which("bwrap") != "/usr/bin/bwrap":
            raise RunnerIsolationError(
                "/usr/bin/bwrap is required; unsandboxed fallback is forbidden"
            )
        if shutil.which("setpriv") != "/usr/bin/setpriv":
            raise RunnerIsolationError("/usr/bin/setpriv is required")

    def command(self, argv: tuple[str, ...]) -> tuple[str, ...]:
        self._validate_argv(argv)
        runner = self.profile.runner
        args = [
            "/usr/bin/setpriv",
            "--no-new-privs",
            "/usr/bin/bwrap",
            "--unshare-all",
            "--unshare-user",
            "--disable-userns",
            "--die-with-parent",
            "--new-session",
            "--clearenv",
            "--uid",
            str(runner.namespace_uid),
            "--gid",
            str(runner.namespace_uid),
            "--cap-drop",
            "ALL",
            "--hostname",
            runner.runner_id,
            "--ro-bind",
            "/usr",
            "/usr",
        ]
        for system_root in (Path("/lib"), Path("/lib64")):
            if system_root.exists():
                args.extend(("--ro-bind", str(system_root), str(system_root)))
        args.extend(("--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp"))
        for key, value in {
            "HOME": "/tmp",
            "LANG": "C.UTF-8",
            "PATH": "/usr/bin",
            "PYTHONDONTWRITEBYTECODE": "1",
            "RUNNER_ACTOR_ID": runner.actor_id,
            "RUNNER_ID": runner.runner_id,
            "RUNNER_ROLE": runner.role,
            "TMPDIR": "/tmp",
        }.items():
            args.extend(("--setenv", key, value))
        if self.workspace is None:
            args.extend(("--chdir", "/tmp"))
        else:
            args.extend(self._workspace_mount_args())
            args.extend(("--chdir", "/workspace"))
        return (*args, "--", *argv)

    def run_json(self, argv: tuple[str, ...], request: dict[str, Any]) -> RunnerResult:
        payload = json.dumps(
            request, ensure_ascii=False, separators=(",", ":"), sort_keys=True
        ).encode("utf-8")
        runner = self.profile.runner
        if len(payload) > runner.max_input_bytes:
            raise RunnerIsolationError("runner input exceeds profile limit")

        def limits() -> None:
            resource.setrlimit(
                resource.RLIMIT_AS,
                (MAX_RUNNER_ADDRESS_SPACE_BYTES, MAX_RUNNER_ADDRESS_SPACE_BYTES),
            )
            resource.setrlimit(
                resource.RLIMIT_FSIZE,
                (runner.max_output_bytes + 1, runner.max_output_bytes + 1),
            )
            resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
            cpu_seconds = max(1, runner.timeout_seconds)
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 1))

        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            try:
                process = subprocess.Popen(
                    self.command(argv),
                    stdin=subprocess.PIPE,
                    stdout=stdout,
                    stderr=stderr,
                    env={},
                    start_new_session=True,
                    preexec_fn=limits,
                )
                process.communicate(payload, timeout=runner.timeout_seconds)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                raise RunnerIsolationError("isolated runner exceeded its timeout") from None
            except OSError as error:
                raise RunnerIsolationError(
                    f"isolated runner could not start: {type(error).__name__}"
                ) from None
            if process.returncode != 0:
                raise RunnerIsolationError(
                    f"isolated runner failed with exit code {process.returncode}"
                )
            if stdout.tell() > runner.max_output_bytes:
                raise RunnerIsolationError("runner output exceeds profile limit")
            stdout.seek(0)
            output = stdout.read()
        try:
            decoded = json.loads(output)
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise RunnerIsolationError("runner output must be one UTF-8 JSON value") from None
        if not isinstance(decoded, dict):
            raise RunnerIsolationError("runner output must be a JSON object")
        return RunnerResult(
            runner_id=runner.runner_id,
            actor_id=runner.actor_id,
            namespace_uid=runner.namespace_uid,
            payload=decoded,
        )

    def _validate_argv(self, argv: tuple[str, ...]) -> None:
        if not argv or len(argv) > MAX_ARGV_ITEMS:
            raise RunnerIsolationError("runner argv count is invalid")
        if argv[0] != "/usr/bin/python3" or len(argv) < 3 or argv[1] != "-I":
            raise RunnerIsolationError("runner entrypoint must be isolated system Python")
        if argv[2] not in {"-c", "-m"}:
            raise RunnerIsolationError("runner Python mode is not allowlisted")
        if any(not isinstance(item, str) or not item or "\x00" in item for item in argv):
            raise RunnerIsolationError("runner argv contains an invalid item")
        if sum(len(item.encode("utf-8")) for item in argv) > MAX_ARGV_BYTES:
            raise RunnerIsolationError("runner argv exceeds size limit")

    def _workspace_mount_args(self) -> list[str]:
        assert self.workspace is not None and self.profile.capability is not None
        workspace = self.workspace
        capability = self.profile.capability
        writable: list[tuple[Path, PurePosixPath]] = []
        for pattern in capability.writable_paths:
            relative = _wildcard_root(pattern)
            source = workspace / relative
            current = workspace
            for part in relative.parts:
                current /= part
                if current.is_symlink():
                    raise RunnerIsolationError("runner writable path contains a symlink")
            if not source.is_dir():
                raise RunnerIsolationError("runner writable root is missing or unsafe")
            resolved = source.resolve(strict=True)
            if not resolved.is_relative_to(workspace):
                raise RunnerIsolationError("runner writable root escaped workspace")
            writable.append((resolved, relative))

        readable: dict[PurePosixPath, Path] = {}
        writable_roots = tuple(item[1] for item in writable)
        for pattern in capability.readable_paths:
            fixed = _wildcard_root(pattern)
            current = workspace
            for part in fixed.parts:
                current /= part
                if current.is_symlink():
                    raise RunnerIsolationError("runner readable path contains a symlink")
            matches = sorted(workspace.glob(pattern))
            if "*" not in pattern and not matches:
                raise RunnerIsolationError("runner required readable path is missing")
            for candidate in matches:
                if candidate.is_dir() and not candidate.is_symlink():
                    continue
                resolved = _safe_match(workspace, candidate)
                relative = PurePosixPath(resolved.relative_to(workspace).as_posix())
                if any(relative.is_relative_to(root) for root in writable_roots):
                    continue
                readable[relative] = resolved

        destinations = [*readable, *(relative for _, relative in writable)]
        directories: set[PurePosixPath] = set()
        for relative in destinations:
            parent = PurePosixPath("/workspace") / relative.parent
            directories.update((parent, *parent.parents))
        mount_args: list[str] = ["--tmpfs", "/workspace"]
        for directory in sorted(
            (item for item in directories if str(item).startswith("/workspace")),
            key=lambda item: (len(item.parts), str(item)),
        ):
            mount_args.extend(("--dir", str(directory)))
        for relative, source in sorted(readable.items(), key=lambda item: str(item[0])):
            mount_args.extend(("--ro-bind", str(source), f"/workspace/{relative}"))
        for source, relative in sorted(writable, key=lambda item: str(item[1])):
            mount_args.extend(("--bind", str(source), f"/workspace/{relative}"))
        mount_args.extend(("--remount-ro", "/workspace"))
        return mount_args
