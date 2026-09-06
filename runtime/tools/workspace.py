"""Scenario-bound workspace reads and atomic writes with retained evidence."""

from __future__ import annotations

import json
import os
import stat
import tempfile
import time
from collections.abc import Callable
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path, PurePosixPath

from contracts import (
    ArtifactReference,
    ToolCallEvidence,
    ToolCallStatus,
    ToolRequest,
    ToolResult,
    WorkspaceReadCall,
    WorkspaceWriteCall,
    tool_arguments_sha256,
)
from policies import (
    CapabilityProfile,
    PolicyCode,
    ToolPolicyDecision,
    ToolUsage,
    authorize_tool_call,
)
from runtime.scenario_harness import HarnessError, ScenarioManifest, verify_workspace

Clock = Callable[[], datetime]
Timer = Callable[[], float]


class WorkspaceBoundaryError(RuntimeError):
    """Filesystem state violated a verified workspace boundary."""


class WorkspaceAuthorizationError(WorkspaceBoundaryError):
    """The deterministic capability policy denied a workspace call."""

    def __init__(self, decision: ToolPolicyDecision) -> None:
        super().__init__(f"{decision.code.value}: {decision.reason}")
        self.decision = decision


def _sha256(contents: bytes) -> str:
    return sha256(contents).hexdigest()


class WorkspaceToolAdapter:
    """Execute only authorized workspace calls in one managed scenario."""

    def __init__(
        self,
        repository_root: Path,
        manifest: ScenarioManifest,
        profile: CapabilityProfile,
        *,
        requested_state_root: Path | None = None,
        clock: Clock | None = None,
        timer: Timer | None = None,
    ) -> None:
        try:
            repository = repository_root.resolve(strict=True)
        except OSError as error:
            raise WorkspaceBoundaryError(
                f"repository root cannot be resolved: {type(error).__name__}"
            ) from None
        if repository_root.is_symlink() or not repository.is_dir():
            raise WorkspaceBoundaryError("repository root must be a real directory")
        if any(
            pattern not in manifest.workspace.editable_paths for pattern in profile.writable_paths
        ):
            raise WorkspaceBoundaryError("profile write scope exceeds the scenario manifest")
        if (
            profile.max_tool_calls > manifest.budgets["tool_calls"]
            or profile.max_wall_time_seconds > manifest.budgets["wall_time_seconds"]
        ):
            raise WorkspaceBoundaryError("profile budgets exceed the scenario manifest")
        self._repository = repository
        self._manifest = manifest
        self._profile = profile
        self._state_root = requested_state_root
        self._clock = clock or (lambda: datetime.now(UTC))
        self._timer = timer or time.monotonic

    def execute(self, request: ToolRequest, usage: ToolUsage) -> ToolResult:
        """Re-authorize and execute a single workspace read or write."""

        decision = authorize_tool_call(self._profile, request, usage)
        if not decision.allowed:
            raise WorkspaceAuthorizationError(decision)
        if not isinstance(request.call, (WorkspaceReadCall, WorkspaceWriteCall)):
            raise WorkspaceBoundaryError("workspace adapter received a non-workspace tool")

        started_at = self._clock()
        started_timer = self._timer()
        workspace = self._verified_workspace()
        if isinstance(request.call, WorkspaceReadCall):
            content, content_type = self._read(workspace, request.call)
        else:
            content, content_type = self._prepare_and_write(
                workspace,
                request.call,
                usage,
            )
        output = content.encode("utf-8")
        self._require_output_budget(output, usage)
        completed_at = self._clock()
        duration_ms = max(0, int((self._timer() - started_timer) * 1_000))
        return self._retain_result(
            request,
            output,
            content_type,
            started_at,
            completed_at,
            duration_ms,
            workspace,
        )

    def _verified_workspace(self) -> Path:
        try:
            status = verify_workspace(
                self._repository,
                self._manifest,
                requested_state_root=self._state_root,
            )
        except HarnessError as error:
            raise WorkspaceBoundaryError(str(error)) from None
        workspace = Path(str(status["workspace"]))
        if workspace.is_symlink() or not workspace.is_dir():
            raise WorkspaceBoundaryError("verified workspace must be a real directory")
        return workspace.resolve(strict=True)

    def _candidate(self, workspace: Path, relative_text: str, *, allow_missing: bool) -> Path:
        relative = PurePosixPath(relative_text)
        candidate = workspace
        for index, part in enumerate(relative.parts):
            candidate /= part
            if candidate.is_symlink():
                raise WorkspaceBoundaryError(f"workspace path contains a symlink: {relative_text}")
            if candidate.exists():
                if index < len(relative.parts) - 1 and not candidate.is_dir():
                    raise WorkspaceBoundaryError(
                        f"workspace path parent is not a directory: {relative_text}"
                    )
            elif not allow_missing:
                raise WorkspaceBoundaryError(f"workspace file does not exist: {relative_text}")
        try:
            parent = candidate.parent.resolve(strict=True)
        except OSError as error:
            if not allow_missing:
                raise WorkspaceBoundaryError(
                    f"workspace path cannot be resolved: {type(error).__name__}"
                ) from None
            parent = candidate.parent
        if parent.exists() and not parent.is_relative_to(workspace):
            raise WorkspaceBoundaryError("workspace path escaped its root")
        return candidate

    def _read(self, workspace: Path, call: WorkspaceReadCall) -> tuple[str, str]:
        candidate = self._candidate(workspace, call.path, allow_missing=False)
        try:
            before = candidate.stat(follow_symlinks=False)
            if not stat.S_ISREG(before.st_mode):
                raise WorkspaceBoundaryError(f"workspace path is not a regular file: {call.path}")
            if before.st_size > self._profile.max_read_bytes:
                raise WorkspaceBoundaryError("workspace read exceeds the profile byte limit")
            contents = candidate.read_bytes()
            after = candidate.stat(follow_symlinks=False)
            text = contents.decode("utf-8")
        except WorkspaceBoundaryError:
            raise
        except (OSError, UnicodeDecodeError) as error:
            raise WorkspaceBoundaryError(
                f"workspace file is not stable UTF-8: {type(error).__name__}"
            ) from None
        before_identity = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        after_identity = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        if before_identity != after_identity or len(contents) != before.st_size:
            raise WorkspaceBoundaryError("workspace file changed while reading")
        return text, "text/plain; charset=utf-8"

    def _prepare_and_write(
        self,
        workspace: Path,
        call: WorkspaceWriteCall,
        usage: ToolUsage,
    ) -> tuple[str, str]:
        candidate = self._candidate(workspace, call.path, allow_missing=True)
        self._create_safe_parents(workspace, candidate.parent)
        previous_hash: str | None = None
        if candidate.exists():
            if candidate.is_symlink():
                raise WorkspaceBoundaryError(f"workspace target is a symlink: {call.path}")
            before = candidate.stat(follow_symlinks=False)
            if not stat.S_ISREG(before.st_mode):
                raise WorkspaceBoundaryError(f"workspace target is not a regular file: {call.path}")
            previous_hash = _sha256(candidate.read_bytes())

        contents = call.content.encode("utf-8")
        content_hash = _sha256(contents)
        response = json.dumps(
            {
                "changed": previous_hash != content_hash,
                "path": call.path,
                "previous_sha256": previous_hash,
                "sha256": content_hash,
                "size_bytes": len(contents),
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        self._require_output_budget(response.encode("utf-8"), usage)
        if previous_hash != content_hash:
            self._write_atomic(candidate, contents)
        try:
            stored = candidate.read_bytes()
            stored_stat = candidate.stat(follow_symlinks=False)
        except OSError as error:
            raise WorkspaceBoundaryError(
                f"workspace write cannot be verified: {type(error).__name__}"
            ) from None
        if not stat.S_ISREG(stored_stat.st_mode) or stored != contents:
            raise WorkspaceBoundaryError("workspace write postcondition failed")
        self._verified_workspace()
        return response, "application/json"

    def _create_safe_parents(self, workspace: Path, parent: Path) -> None:
        try:
            relative = parent.relative_to(workspace)
        except ValueError:
            raise WorkspaceBoundaryError("workspace parent escaped its root") from None
        current = workspace
        for part in relative.parts:
            current /= part
            if current.is_symlink():
                raise WorkspaceBoundaryError("workspace parent contains a symlink")
            try:
                current.mkdir(mode=0o755)
            except FileExistsError:
                pass
            except OSError as error:
                raise WorkspaceBoundaryError(
                    f"workspace parent cannot be created: {type(error).__name__}"
                ) from None
            if not current.is_dir() or current.is_symlink():
                raise WorkspaceBoundaryError("workspace parent is not a real directory")

    def _write_atomic(self, target: Path, contents: bytes) -> None:
        descriptor, temporary_text = tempfile.mkstemp(prefix=".agent-write-", dir=target.parent)
        temporary = Path(temporary_text)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(contents)
                stream.flush()
                os.fsync(stream.fileno())
                os.fchmod(stream.fileno(), 0o644)
            if target.is_symlink():
                raise WorkspaceBoundaryError("workspace target became a symlink")
            os.replace(temporary, target)
        except Exception:
            if temporary.exists():
                temporary.unlink()
            raise

    def _require_output_budget(self, output: bytes, usage: ToolUsage) -> None:
        if usage.output_bytes + len(output) > self._profile.max_output_bytes:
            raise WorkspaceAuthorizationError(
                ToolPolicyDecision(
                    allowed=False,
                    code=PolicyCode.BUDGET_DENIED,
                    reason="tool output would exceed the remaining byte budget",
                )
            )

    def _retain_result(
        self,
        request: ToolRequest,
        output: bytes,
        content_type: str,
        started_at: datetime,
        completed_at: datetime,
        duration_ms: int,
        workspace: Path,
    ) -> ToolResult:
        output_hash = _sha256(output)
        suffix = ".json" if content_type == "application/json" else ".txt"
        state_root = workspace.parents[1]
        evidence_directory = state_root / "evidence/tool-calls"
        self._ensure_evidence_directory(state_root, evidence_directory)
        artifact_path = evidence_directory / f"{output_hash}{suffix}"
        self._retain_content(artifact_path, output)
        relative_artifact = artifact_path.relative_to(self._repository).as_posix()
        artifact = ArtifactReference(
            path=relative_artifact,
            sha256=output_hash,
            media_type=content_type,
            size_bytes=len(output),
        )
        evidence_id = (
            f"tool-{sha256(f'{request.task_id}:{request.request_id}'.encode()).hexdigest()[:24]}"
        )
        evidence = ToolCallEvidence(
            evidence_id=evidence_id,
            request_id=request.request_id,
            task_id=request.task_id,
            producer_id="workspace-adapter",
            tool=request.call.tool,
            arguments_sha256=tool_arguments_sha256(request.call),
            started_at=started_at,
            completed_at=completed_at,
            status=ToolCallStatus.SUCCESS,
            exit_code=0,
            duration_ms=duration_ms,
            output_bytes=len(output),
            output=artifact,
        )
        return ToolResult(
            request_id=request.request_id,
            task_id=request.task_id,
            tool=request.call.tool,
            content=output.decode("utf-8"),
            content_type=content_type,
            size_bytes=len(output),
            sha256=output_hash,
            evidence=evidence,
        )

    def _ensure_evidence_directory(self, state_root: Path, target: Path) -> None:
        current = state_root
        for part in target.relative_to(state_root).parts:
            current /= part
            if current.is_symlink():
                raise WorkspaceBoundaryError("evidence path contains a symlink")
            try:
                current.mkdir(mode=0o700)
            except FileExistsError:
                pass
            except OSError as error:
                raise WorkspaceBoundaryError(
                    f"evidence directory cannot be created: {type(error).__name__}"
                ) from None
            if not current.is_dir() or current.is_symlink():
                raise WorkspaceBoundaryError("evidence path is not a real directory")

    def _retain_content(self, target: Path, contents: bytes) -> None:
        if target.exists() or target.is_symlink():
            if target.is_symlink() or not target.is_file() or target.read_bytes() != contents:
                raise WorkspaceBoundaryError("content-addressed evidence path is inconsistent")
            return
        descriptor, temporary_text = tempfile.mkstemp(prefix=".evidence-", dir=target.parent)
        temporary = Path(temporary_text)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(contents)
                stream.flush()
                os.fsync(stream.fileno())
                os.fchmod(stream.fileno(), 0o600)
            try:
                os.link(temporary, target, follow_symlinks=False)
            except FileExistsError:
                if target.is_symlink() or not target.is_file() or target.read_bytes() != contents:
                    raise WorkspaceBoundaryError("content-addressed evidence path raced") from None
        finally:
            if temporary.exists():
                temporary.unlink()
