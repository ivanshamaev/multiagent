"""Secure content-addressed retention for deterministic tool evidence."""

from __future__ import annotations

import os
import tempfile
from datetime import datetime
from hashlib import sha256
from pathlib import Path

from contracts import (
    ArtifactReference,
    ToolCallEvidence,
    ToolCallStatus,
    ToolRequest,
    ToolResult,
    tool_arguments_sha256,
)


class EvidenceStoreError(RuntimeError):
    """The repository-local evidence boundary is missing or unsafe."""


class ToolEvidenceStore:
    """Retain bounded outputs below one repository-local state directory."""

    def __init__(self, repository_root: Path, state_root: Path) -> None:
        try:
            repository = repository_root.resolve(strict=True)
        except OSError as error:
            raise EvidenceStoreError(
                f"repository root cannot be resolved: {type(error).__name__}"
            ) from None
        if repository_root.is_symlink() or not repository.is_dir():
            raise EvidenceStoreError("repository root must be a real directory")
        state = state_root if state_root.is_absolute() else repository / state_root
        if state.is_symlink():
            raise EvidenceStoreError("evidence state root must not be a symlink")
        try:
            state.mkdir(mode=0o700, exist_ok=True)
            state = state.resolve(strict=True)
        except OSError as error:
            raise EvidenceStoreError(
                f"evidence state root cannot be prepared: {type(error).__name__}"
            ) from None
        if not state.is_dir() or not state.is_relative_to(repository):
            raise EvidenceStoreError("evidence state root must stay inside the repository")
        self._repository = repository
        self._directory = state / "evidence/tool-calls"
        self._ensure_directory(state, self._directory)

    def success_result(
        self,
        request: ToolRequest,
        output: bytes,
        content_type: str,
        *,
        producer_id: str,
        started_at: datetime,
        completed_at: datetime,
        duration_ms: int,
    ) -> ToolResult:
        """Retain a successful output and bind it to its typed request."""

        artifact = self._retain_artifact(output, content_type)
        evidence = self.outcome(
            request,
            status=ToolCallStatus.SUCCESS,
            producer_id=producer_id,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            exit_code=0,
            artifact=artifact,
        )
        return ToolResult(
            request_id=request.request_id,
            task_id=request.task_id,
            tool=request.call.tool,
            content=output.decode("utf-8"),
            content_type=content_type,
            size_bytes=len(output),
            sha256=artifact.sha256,
            evidence=evidence,
        )

    def error_with_output(
        self,
        request: ToolRequest,
        output: bytes,
        content_type: str,
        *,
        producer_id: str,
        started_at: datetime,
        completed_at: datetime,
        duration_ms: int,
        error_type: str,
    ) -> ToolCallEvidence:
        """Retain bounded diagnostic output for a failed remote invocation."""

        artifact = self._retain_artifact(output, content_type)
        return self.outcome(
            request,
            status=ToolCallStatus.ERROR,
            producer_id=producer_id,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            exit_code=1,
            artifact=artifact,
            error_type=error_type,
        )

    def outcome(
        self,
        request: ToolRequest,
        *,
        status: ToolCallStatus,
        producer_id: str,
        started_at: datetime,
        completed_at: datetime,
        duration_ms: int,
        exit_code: int | None = None,
        artifact: ArtifactReference | None = None,
        error_type: str | None = None,
    ) -> ToolCallEvidence:
        """Create metadata for an outcome; denied/timeout paths retain no server output."""

        evidence_seed = f"{request.task_id}:{request.request_id}:{status.value}"
        return ToolCallEvidence(
            evidence_id=f"tool-{sha256(evidence_seed.encode()).hexdigest()[:24]}",
            request_id=request.request_id,
            task_id=request.task_id,
            producer_id=producer_id,
            tool=request.call.tool,
            arguments_sha256=tool_arguments_sha256(request.call),
            started_at=started_at,
            completed_at=completed_at,
            status=status,
            exit_code=exit_code,
            duration_ms=duration_ms,
            output_bytes=0 if artifact is None else artifact.size_bytes,
            output=artifact,
            error_type=error_type,
        )

    def _retain_artifact(self, contents: bytes, content_type: str) -> ArtifactReference:
        output_hash = sha256(contents).hexdigest()
        suffix = ".json" if content_type == "application/json" else ".txt"
        target = self._directory / f"{output_hash}{suffix}"
        self._retain_content(target, contents)
        return ArtifactReference(
            path=target.relative_to(self._repository).as_posix(),
            sha256=output_hash,
            media_type=content_type,
            size_bytes=len(contents),
        )

    @staticmethod
    def _ensure_directory(state_root: Path, target: Path) -> None:
        current = state_root
        for part in target.relative_to(state_root).parts:
            current /= part
            if current.is_symlink():
                raise EvidenceStoreError("evidence path contains a symlink")
            try:
                current.mkdir(mode=0o700)
            except FileExistsError:
                pass
            except OSError as error:
                raise EvidenceStoreError(
                    f"evidence directory cannot be created: {type(error).__name__}"
                ) from None
            if not current.is_dir() or current.is_symlink():
                raise EvidenceStoreError("evidence path is not a real directory")

    @staticmethod
    def _retain_content(target: Path, contents: bytes) -> None:
        if target.exists() or target.is_symlink():
            if target.is_symlink() or not target.is_file() or target.read_bytes() != contents:
                raise EvidenceStoreError("content-addressed evidence path is inconsistent")
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
                    raise EvidenceStoreError("content-addressed evidence path raced") from None
        finally:
            if temporary.exists():
                temporary.unlink()
