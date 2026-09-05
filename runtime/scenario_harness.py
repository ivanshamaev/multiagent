"""Deterministic, fail-closed lifecycle for local evaluation scenarios."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path, PurePosixPath
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
STATE_DIRECTORY_NAME = ".scenario-state"
SENTINEL_NAME = ".scenario-workspace.json"
PUBLIC_MANIFEST_PATH = ".scenario/manifest.json"
MANAGED_BY = "agentic-data-platform-scenario-harness"
SCENARIO_ID_CHARACTERS = frozenset("abcdefghijklmnopqrstuvwxyz0123456789-")


class ExitCode(IntEnum):
    """Stable process interface used by Make and future orchestration code."""

    OK = 0
    INVALID_STATE = 20
    STALE_SOURCE = 21
    PROTECTED_CHANGE = 22
    UNSAFE_PATH = 23


class HarnessError(RuntimeError):
    """Base error with a deterministic exit code."""

    exit_code = ExitCode.INVALID_STATE


class StaleSourceError(HarnessError):
    """The source allowlist changed after the last reset."""

    exit_code = ExitCode.STALE_SOURCE


class ProtectedChangeError(HarnessError):
    """The candidate changed a path outside its editable allowlist."""

    exit_code = ExitCode.PROTECTED_CHANGE


class UnsafePathError(HarnessError):
    """A path could escape or ambiguously address the managed workspace."""

    exit_code = ExitCode.UNSAFE_PATH


@dataclass(frozen=True)
class SourceConfig:
    commit: str
    snapshot_paths: tuple[str, ...]
    excluded_names: tuple[str, ...]


@dataclass(frozen=True)
class WorkspaceConfig:
    editable_paths: tuple[str, ...]
    required_paths: tuple[str, ...]


@dataclass(frozen=True)
class HiddenGradeConfig:
    interface_version: int
    command: str
    container_service: str
    oracle_sha256: str


@dataclass(frozen=True)
class ScenarioManifest:
    schema_version: int
    scenario_id: str
    version: str
    task_file: str
    source: SourceConfig
    workspace: WorkspaceConfig
    budgets: dict[str, int]
    setup_commands: tuple[str, ...]
    public_commands: tuple[str, ...]
    hidden_grade: HiddenGradeConfig


@dataclass(frozen=True)
class Baseline:
    source_fingerprint: str
    baseline_fingerprint: str
    files: dict[str, str]
    contents: dict[str, bytes]


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise HarnessError(f"{field} must be an object")
    return value


def _exact_keys(value: dict[str, Any], expected: set[str], field: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise HarnessError(f"{field} keys mismatch: missing={missing}, extra={extra}")


def _string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise HarnessError(f"{field} must be a non-empty string")
    return value


def _integer(value: Any, field: str, *, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise HarnessError(f"{field} must be an integer >= {minimum}")
    return value


def _strings(value: Any, field: str, *, non_empty: bool = True) -> tuple[str, ...]:
    if not isinstance(value, list) or (non_empty and not value):
        raise HarnessError(f"{field} must be a non-empty array")
    result = tuple(_string(item, f"{field}[]") for item in value)
    if len(result) != len(set(result)):
        raise HarnessError(f"{field} must not contain duplicates")
    return result


def validate_scenario_id(value: str) -> str:
    """Reject traversal and ambiguous scenario identifiers."""

    if (
        not value
        or value[0] == "-"
        or value[-1] == "-"
        or "--" in value
        or any(character not in SCENARIO_ID_CHARACTERS for character in value)
    ):
        raise UnsafePathError("scenario id must use lowercase kebab-case")
    return value


def validate_relative_path(value: str, field: str) -> str:
    """Return a canonical repository-relative POSIX path or fail closed."""

    _string(value, field)
    if "\\" in value or value.startswith("/"):
        raise UnsafePathError(f"{field} must be a relative POSIX path")
    raw_parts = value.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        raise UnsafePathError(f"{field} contains an unsafe path component")
    path = PurePosixPath(value)
    if path.is_absolute():
        raise UnsafePathError(f"{field} must be relative")
    return path.as_posix()


def _commands(value: Any, field: str) -> tuple[str, ...]:
    command_object = _object(value, field)
    _exact_keys(command_object, {"commands"}, field)
    commands = _strings(command_object["commands"], f"{field}.commands")
    if any("\n" in command or "\r" in command for command in commands):
        raise HarnessError(f"{field}.commands must be one line each")
    return commands


def parse_manifest(payload: Any) -> ScenarioManifest:
    """Strictly validate the version-one manifest without optional dependencies."""

    root = _object(payload, "manifest")
    _exact_keys(
        root,
        {
            "schema_version",
            "id",
            "version",
            "task_file",
            "source",
            "workspace",
            "budgets",
            "setup",
            "public_validation",
            "hidden_grade",
        },
        "manifest",
    )
    if root["schema_version"] != 1:
        raise HarnessError("only scenario schema_version 1 is supported")

    scenario_id = validate_scenario_id(_string(root["id"], "id"))
    version = _string(root["version"], "version")
    version_parts = version.split(".")
    if len(version_parts) != 3 or any(not part.isdigit() for part in version_parts):
        raise HarnessError("version must use MAJOR.MINOR.PATCH")
    task_file = validate_relative_path(_string(root["task_file"], "task_file"), "task_file")

    source_payload = _object(root["source"], "source")
    _exact_keys(source_payload, {"commit", "snapshot_paths", "excluded_names"}, "source")
    commit = _string(source_payload["commit"], "source.commit")
    if len(commit) != 40 or any(character not in "0123456789abcdef" for character in commit):
        raise HarnessError("source.commit must be a full lowercase Git SHA")
    snapshot_paths = tuple(
        validate_relative_path(path, "source.snapshot_paths[]")
        for path in _strings(source_payload["snapshot_paths"], "source.snapshot_paths")
    )
    forbidden_roots = {".git", ".scenario-state", "grader", "plan"}
    if any(path.split("/", maxsplit=1)[0] in forbidden_roots for path in snapshot_paths):
        raise HarnessError("source.snapshot_paths includes a protected repository root")
    excluded_names = _strings(
        source_payload["excluded_names"], "source.excluded_names", non_empty=False
    )
    if any(name in {".", ".."} or "/" in name or "\\" in name for name in excluded_names):
        raise HarnessError("source.excluded_names must contain base names only")

    workspace_payload = _object(root["workspace"], "workspace")
    _exact_keys(workspace_payload, {"editable_paths", "required_paths"}, "workspace")
    editable_paths = _strings(workspace_payload["editable_paths"], "workspace.editable_paths")
    for path in editable_paths:
        if not path.endswith("/**"):
            raise HarnessError("workspace.editable_paths entries must end with /**")
        validate_relative_path(path.removesuffix("/**"), "workspace.editable_paths[]")
    required_paths = tuple(
        validate_relative_path(path, "workspace.required_paths[]")
        for path in _strings(workspace_payload["required_paths"], "workspace.required_paths")
    )

    budgets_payload = _object(root["budgets"], "budgets")
    budget_fields = {"wall_time_seconds", "tool_calls", "model_tokens", "rework_attempts"}
    _exact_keys(budgets_payload, budget_fields, "budgets")
    budgets = {
        field: _integer(
            budgets_payload[field],
            f"budgets.{field}",
            minimum=0 if field == "rework_attempts" else 1,
        )
        for field in sorted(budget_fields)
    }

    hidden_payload = _object(root["hidden_grade"], "hidden_grade")
    _exact_keys(
        hidden_payload,
        {"interface_version", "command", "container_service", "oracle_sha256"},
        "hidden_grade",
    )
    if hidden_payload["interface_version"] != 1:
        raise HarnessError("only hidden grade interface_version 1 is supported")
    oracle_hash = _string(hidden_payload["oracle_sha256"], "hidden_grade.oracle_sha256")
    if len(oracle_hash) != 64 or any(
        character not in "0123456789abcdef" for character in oracle_hash
    ):
        raise HarnessError("hidden_grade.oracle_sha256 must be a lowercase SHA-256")

    return ScenarioManifest(
        schema_version=1,
        scenario_id=scenario_id,
        version=version,
        task_file=task_file,
        source=SourceConfig(commit, snapshot_paths, excluded_names),
        workspace=WorkspaceConfig(editable_paths, required_paths),
        budgets=budgets,
        setup_commands=_commands(root["setup"], "setup"),
        public_commands=_commands(root["public_validation"], "public_validation"),
        hidden_grade=HiddenGradeConfig(
            interface_version=1,
            command=_string(hidden_payload["command"], "hidden_grade.command"),
            container_service=_string(
                hidden_payload["container_service"], "hidden_grade.container_service"
            ),
            oracle_sha256=oracle_hash,
        ),
    )


def load_manifest(repository_root: Path, scenario_id: str) -> ScenarioManifest:
    """Load the requested manifest from the canonical scenarios directory."""

    scenario_id = validate_scenario_id(scenario_id)
    path = repository_root.resolve() / "scenarios" / scenario_id / "manifest.json"
    if path.is_symlink() or not path.is_file():
        raise HarnessError(f"manifest not found for scenario {scenario_id}")
    try:
        manifest = parse_manifest(json.loads(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise HarnessError("manifest is not valid UTF-8 JSON") from error
    if manifest.scenario_id != scenario_id:
        raise HarnessError("manifest id does not match its directory")
    return manifest


def _sha256(contents: bytes) -> str:
    return hashlib.sha256(contents).hexdigest()


def _fingerprint(files: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for path, content_hash in sorted(files.items()):
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(content_hash.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _inside(root: Path, candidate: Path) -> bool:
    return candidate == root or candidate.is_relative_to(root)


def _source_files(repository_root: Path, manifest: ScenarioManifest) -> dict[str, bytes]:
    root = repository_root.resolve()
    excluded = set(manifest.source.excluded_names)
    contents: dict[str, bytes] = {}

    for relative_text in manifest.source.snapshot_paths:
        relative = PurePosixPath(relative_text)
        source = root.joinpath(*relative.parts)
        resolved = source.resolve()
        if not _inside(root, resolved) or source.is_symlink():
            raise UnsafePathError(f"snapshot source is unsafe: {relative_text}")
        if source.is_file():
            if source.name not in excluded:
                contents[relative.as_posix()] = source.read_bytes()
            continue
        if not source.is_dir():
            raise HarnessError(f"snapshot source is missing: {relative_text}")

        for current_text, directory_names, file_names in os.walk(source, followlinks=False):
            current = Path(current_text)
            safe_directories: list[str] = []
            for name in sorted(directory_names):
                child = current / name
                if child.is_symlink():
                    raise UnsafePathError(f"symlink is forbidden in snapshot: {name}")
                if name not in excluded:
                    safe_directories.append(name)
            directory_names[:] = safe_directories
            for name in sorted(file_names):
                child = current / name
                if child.is_symlink():
                    raise UnsafePathError(f"symlink is forbidden in snapshot: {name}")
                if name in excluded:
                    continue
                mode = child.stat().st_mode
                if not stat.S_ISREG(mode):
                    raise UnsafePathError(f"non-regular snapshot file is forbidden: {name}")
                target = child.relative_to(root).as_posix()
                if target in contents:
                    raise HarnessError(f"overlapping snapshot paths contain {target}")
                contents[target] = child.read_bytes()

    task_path = root.joinpath(*PurePosixPath(manifest.task_file).parts)
    if task_path.is_symlink() or not task_path.is_file() or not _inside(root, task_path.resolve()):
        raise UnsafePathError("task_file is missing or unsafe")
    contents["TASK.md"] = task_path.read_bytes()
    return contents


def _public_manifest(manifest: ScenarioManifest, source_fingerprint: str) -> bytes:
    payload = {
        "schema_version": manifest.schema_version,
        "id": manifest.scenario_id,
        "version": manifest.version,
        "source": {
            "commit": manifest.source.commit,
            "fingerprint": source_fingerprint,
        },
        "workspace": {"editable_paths": list(manifest.workspace.editable_paths)},
        "budgets": manifest.budgets,
        "public_validation": {"commands": list(manifest.public_commands)},
        "hidden_grade": {
            "interface_version": manifest.hidden_grade.interface_version,
            "command": manifest.hidden_grade.command,
        },
    }
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


def build_baseline(repository_root: Path, manifest: ScenarioManifest) -> Baseline:
    """Build an in-memory, content-addressed baseline from the source allowlist."""

    contents = _source_files(repository_root, manifest)
    source_hashes = {path: _sha256(value) for path, value in contents.items()}
    source_fingerprint = _fingerprint(source_hashes)
    contents[PUBLIC_MANIFEST_PATH] = _public_manifest(manifest, source_fingerprint)
    hashes = {path: _sha256(value) for path, value in contents.items()}
    return Baseline(source_fingerprint, _fingerprint(hashes), hashes, contents)


def _state_root(repository_root: Path, requested: Path | None) -> Path:
    repository = repository_root.resolve()
    candidate = requested if requested is not None else repository / STATE_DIRECTORY_NAME
    resolved = candidate.resolve()
    if resolved.name != STATE_DIRECTORY_NAME or not _inside(repository, resolved):
        raise UnsafePathError(f"state root must be repository-local {STATE_DIRECTORY_NAME}")
    return resolved


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _git_state(repository_root: Path) -> tuple[str | None, bool | None]:
    try:
        head = subprocess.run(
            ["git", "-C", str(repository_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "-C", str(repository_root), "status", "--porcelain=v1"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout
    except (FileNotFoundError, subprocess.SubprocessError):
        return None, None
    return head, bool(status)


def _record_path(state_root: Path, scenario_id: str) -> Path:
    return state_root / "records" / f"{scenario_id}.json"


def _workspace_path(state_root: Path, scenario_id: str) -> Path:
    return state_root / "workspaces" / scenario_id


def _read_json_object(path: Path, field: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise HarnessError(f"{field} is missing")
    try:
        return _object(json.loads(path.read_text(encoding="utf-8")), field)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise HarnessError(f"{field} is invalid") from error


def _assert_managed_workspace(path: Path, state_root: Path, manifest: ScenarioManifest) -> None:
    expected = _workspace_path(state_root, manifest.scenario_id)
    if path != expected or path.is_symlink() or not path.is_dir():
        raise UnsafePathError("refusing to replace a non-canonical workspace")
    sentinel_path = path / SENTINEL_NAME
    if sentinel_path.is_symlink() or not sentinel_path.is_file():
        raise UnsafePathError("refusing to replace a workspace without the exact sentinel")
    try:
        sentinel = _read_json_object(sentinel_path, "workspace sentinel")
    except HarnessError as error:
        raise UnsafePathError(
            "refusing to replace a workspace without the exact sentinel"
        ) from error
    if sentinel != {
        "managed_by": MANAGED_BY,
        "scenario_id": manifest.scenario_id,
        "scenario_version": manifest.version,
    }:
        raise UnsafePathError("refusing to replace a workspace without the exact sentinel")


def _copy_baseline(target: Path, baseline: Baseline, manifest: ScenarioManifest) -> None:
    # tempfile creates 0700; the non-root grader needs read-only traversal.
    target.chmod(0o755)
    for relative_text, contents in sorted(baseline.contents.items()):
        relative = PurePosixPath(relative_text)
        destination = target.joinpath(*relative.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(contents)
    _write_json_atomic(
        target / SENTINEL_NAME,
        {
            "managed_by": MANAGED_BY,
            "scenario_id": manifest.scenario_id,
            "scenario_version": manifest.version,
        },
    )


def reset_workspace(
    repository_root: Path,
    manifest: ScenarioManifest,
    *,
    requested_state_root: Path | None = None,
) -> dict[str, Any]:
    """Transactionally recreate only the exact managed scenario workspace."""

    repository = repository_root.resolve()
    state_root = _state_root(repository, requested_state_root)
    baseline = build_baseline(repository, manifest)
    state_root.mkdir(parents=True, exist_ok=True)
    (state_root / "workspaces").mkdir(exist_ok=True)
    temporary_root = state_root / "tmp"
    temporary_root.mkdir(exist_ok=True)
    lock_path = state_root / ".lock"

    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        temporary = Path(
            tempfile.mkdtemp(prefix=f"{manifest.scenario_id}-new-", dir=temporary_root)
        )
        backup: Path | None = None
        workspace = _workspace_path(state_root, manifest.scenario_id)
        try:
            _copy_baseline(temporary, baseline, manifest)
            if workspace.exists() or workspace.is_symlink():
                _assert_managed_workspace(workspace, state_root, manifest)
                backup = temporary_root / f"{manifest.scenario_id}-previous-{uuid.uuid4().hex}"
                os.replace(workspace, backup)
            os.replace(temporary, workspace)

            head, dirty = _git_state(repository)
            record = {
                "record_version": 1,
                "scenario_id": manifest.scenario_id,
                "scenario_version": manifest.version,
                "declared_source_commit": manifest.source.commit,
                "observed_source_commit": head,
                "observed_source_dirty": dirty,
                "source_fingerprint": baseline.source_fingerprint,
                "baseline_fingerprint": baseline.baseline_fingerprint,
                "files": baseline.files,
                "editable_paths": list(manifest.workspace.editable_paths),
                "excluded_names": list(manifest.source.excluded_names),
                "data_fingerprint": None,
            }
            _write_json_atomic(_record_path(state_root, manifest.scenario_id), record)
            if backup is not None:
                shutil.rmtree(backup)
        except Exception:
            if backup is not None and backup.exists() and not workspace.exists():
                os.replace(backup, workspace)
            raise
        finally:
            if temporary.exists():
                shutil.rmtree(temporary)

    return {
        "baseline_fingerprint": baseline.baseline_fingerprint,
        "scenario_id": manifest.scenario_id,
        "source_fingerprint": baseline.source_fingerprint,
        "workspace": str(workspace),
    }


def _scan_workspace(workspace: Path, excluded_names: set[str]) -> dict[str, str]:
    files: dict[str, str] = {}
    for current_text, directory_names, file_names in os.walk(workspace, followlinks=False):
        current = Path(current_text)
        safe_directories: list[str] = []
        for name in sorted(directory_names):
            child = current / name
            if child.is_symlink():
                raise UnsafePathError(f"workspace contains forbidden symlink: {name}")
            if name not in excluded_names:
                safe_directories.append(name)
        directory_names[:] = safe_directories
        for name in sorted(file_names):
            child = current / name
            if child == workspace / SENTINEL_NAME or name in excluded_names:
                continue
            if child.is_symlink() or not child.is_file():
                raise UnsafePathError(f"workspace contains a non-regular file: {name}")
            relative = child.relative_to(workspace).as_posix()
            files[relative] = _sha256(child.read_bytes())
    return files


def _is_editable(path: str, editable_paths: tuple[str, ...]) -> bool:
    for pattern in editable_paths:
        root = pattern.removesuffix("/**")
        if path.startswith(f"{root}/"):
            return True
    return False


def inspect_workspace(
    repository_root: Path,
    manifest: ScenarioManifest,
    *,
    requested_state_root: Path | None = None,
) -> dict[str, Any]:
    """Compare the candidate with trusted state and classify all drift."""

    repository = repository_root.resolve()
    state_root = _state_root(repository, requested_state_root)
    workspace = _workspace_path(state_root, manifest.scenario_id)
    _assert_managed_workspace(workspace, state_root, manifest)
    record = _read_json_object(_record_path(state_root, manifest.scenario_id), "baseline record")
    if (
        record.get("record_version") != 1
        or record.get("scenario_id") != manifest.scenario_id
        or record.get("scenario_version") != manifest.version
    ):
        raise HarnessError("baseline record does not match the manifest")

    current_baseline = build_baseline(repository, manifest)
    stale = (
        record.get("source_fingerprint") != current_baseline.source_fingerprint
        or record.get("baseline_fingerprint") != current_baseline.baseline_fingerprint
    )
    baseline_files_value = record.get("files")
    if not isinstance(baseline_files_value, dict) or not all(
        isinstance(path, str) and isinstance(value, str)
        for path, value in baseline_files_value.items()
    ):
        raise HarnessError("baseline record files are invalid")
    baseline_files: dict[str, str] = baseline_files_value
    actual_files = _scan_workspace(workspace, set(manifest.source.excluded_names))

    added = sorted(set(actual_files) - set(baseline_files))
    deleted = sorted(set(baseline_files) - set(actual_files))
    modified = sorted(
        path
        for path in set(actual_files) & set(baseline_files)
        if actual_files[path] != baseline_files[path]
    )
    protected = sorted(
        path
        for path in [*added, *deleted, *modified]
        if not _is_editable(path, manifest.workspace.editable_paths)
    )
    missing_required = sorted(
        path
        for path in manifest.workspace.required_paths
        if not (workspace.joinpath(*PurePosixPath(path).parts).is_file())
    )
    protected = sorted(set(protected) | set(missing_required))

    return {
        "actual_fingerprint": _fingerprint(actual_files),
        "added": added,
        "baseline_fingerprint": record["baseline_fingerprint"],
        "data_fingerprint": record.get("data_fingerprint"),
        "deleted": deleted,
        "modified": modified,
        "ok": not stale and not protected,
        "protected_violations": protected,
        "scenario_id": manifest.scenario_id,
        "source_fingerprint": record["source_fingerprint"],
        "stale_source": stale,
        "workspace": str(workspace),
    }


def verify_workspace(
    repository_root: Path,
    manifest: ScenarioManifest,
    *,
    requested_state_root: Path | None = None,
) -> dict[str, Any]:
    """Fail with a stable class when source or protected candidate state drifted."""

    status = inspect_workspace(repository_root, manifest, requested_state_root=requested_state_root)
    if status["stale_source"]:
        raise StaleSourceError("scenario source changed; run scenario-reset")
    if status["protected_violations"]:
        paths = ", ".join(status["protected_violations"])
        raise ProtectedChangeError(f"protected workspace paths changed: {paths}")
    return status


def record_data_fingerprint(
    repository_root: Path,
    manifest: ScenarioManifest,
    logical_snapshot: bytes,
    *,
    requested_state_root: Path | None = None,
) -> dict[str, Any]:
    """Attach a logical ClickHouse snapshot hash to the trusted reset record."""

    if not logical_snapshot.strip():
        raise HarnessError("logical data snapshot is empty")
    if len(logical_snapshot) > 5_000_000:
        raise HarnessError("logical data snapshot is unexpectedly large")
    state_root = _state_root(repository_root.resolve(), requested_state_root)
    verify_workspace(repository_root, manifest, requested_state_root=state_root)
    path = _record_path(state_root, manifest.scenario_id)
    record = _read_json_object(path, "baseline record")
    previous = record.get("data_fingerprint")
    current = _sha256(logical_snapshot)
    record["data_fingerprint"] = current
    _write_json_atomic(path, record)
    return {
        "data_fingerprint": current,
        "matches_previous_record": previous in {None, current},
        "scenario_id": manifest.scenario_id,
    }


def verify_oracle(repository_root: Path, manifest: ScenarioManifest) -> dict[str, Any]:
    """Verify the packaged human-authored oracle before building its image."""

    oracle = repository_root.resolve() / "grader" / "hidden" / "grade.py"
    if oracle.is_symlink() or not oracle.is_file():
        raise HarnessError("hidden grader oracle is missing")
    actual = _sha256(oracle.read_bytes())
    if actual != manifest.hidden_grade.oracle_sha256:
        raise StaleSourceError("hidden grader oracle hash does not match the manifest")
    return {"oracle_sha256": actual, "scenario_id": manifest.scenario_id}


def reproducibility_fingerprint(
    repository_root: Path,
    manifest: ScenarioManifest,
    *,
    requested_state_root: Path | None = None,
) -> dict[str, Any]:
    """Return only stable reset outputs suitable for exact comparison."""

    status = verify_workspace(repository_root, manifest, requested_state_root=requested_state_root)
    if status["data_fingerprint"] is None:
        raise HarnessError("data fingerprint has not been recorded")
    return {
        "baseline_fingerprint": status["baseline_fingerprint"],
        "data_fingerprint": status["data_fingerprint"],
        "scenario_id": manifest.scenario_id,
        "source_fingerprint": status["source_fingerprint"],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("reset", "status", "verify", "record-data", "fingerprint", "verify-oracle"),
    )
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--state-root", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the scenario lifecycle CLI without leaking hidden grader contents."""

    arguments = _parser().parse_args(argv)
    try:
        manifest = load_manifest(REPOSITORY_ROOT, arguments.scenario)
        kwargs = {"requested_state_root": arguments.state_root}
        if arguments.command == "reset":
            result = reset_workspace(REPOSITORY_ROOT, manifest, **kwargs)
        elif arguments.command == "status":
            result = inspect_workspace(REPOSITORY_ROOT, manifest, **kwargs)
            if result["stale_source"]:
                print(json.dumps(result, sort_keys=True))
                return ExitCode.STALE_SOURCE
            if result["protected_violations"]:
                print(json.dumps(result, sort_keys=True))
                return ExitCode.PROTECTED_CHANGE
        elif arguments.command == "verify":
            result = verify_workspace(REPOSITORY_ROOT, manifest, **kwargs)
        elif arguments.command == "record-data":
            result = record_data_fingerprint(
                REPOSITORY_ROOT, manifest, sys.stdin.buffer.read(), **kwargs
            )
        elif arguments.command == "fingerprint":
            result = reproducibility_fingerprint(REPOSITORY_ROOT, manifest, **kwargs)
        else:
            result = verify_oracle(REPOSITORY_ROOT, manifest)
        print(json.dumps(result, sort_keys=True))
        return ExitCode.OK
    except HarnessError as error:
        print(
            json.dumps(
                {"error": error.__class__.__name__, "message": str(error), "ok": False},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return error.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
