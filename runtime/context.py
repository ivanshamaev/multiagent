"""Bounded, content-addressed context from a verified scenario workspace."""

from __future__ import annotations

import stat
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Annotated

from pydantic import ConfigDict, Field, StringConstraints, TypeAdapter, model_validator

from contracts.common import FrozenModel, NonNegativeInt, RelativePath, Sha256, ensure_unique
from runtime.scenario_harness import load_manifest, verify_workspace

ContextText = Annotated[str, StringConstraints(max_length=100_000)]
PROTECTED_NAMES = frozenset(
    {".env", ".git", ".scenario-state", ".scenario-workspace.json", "grader", "plan"}
)
RELATIVE_PATH_ADAPTER = TypeAdapter(RelativePath)


class ContextBoundaryError(RuntimeError):
    """Context selection crossed a filesystem or size boundary."""


class ContextDocument(FrozenModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=False,
        validate_default=True,
    )

    path: RelativePath
    content: ContextText = Field(repr=False)
    size_bytes: NonNegativeInt
    sha256: Sha256

    @model_validator(mode="after")
    def validate_content_address(self):
        encoded = self.content.encode("utf-8")
        if self.size_bytes != len(encoded):
            raise ValueError("context size does not match UTF-8 content")
        if self.sha256 != sha256(encoded).hexdigest():
            raise ValueError("context SHA-256 does not match content")
        return self


class ContextBundle(FrozenModel):
    workspace_fingerprint: Sha256
    documents: tuple[ContextDocument, ...] = Field(min_length=1, max_length=32)
    total_bytes: NonNegativeInt

    @model_validator(mode="after")
    def validate_bundle(self):
        ensure_unique(tuple(document.path for document in self.documents), "context paths")
        if self.total_bytes != sum(document.size_bytes for document in self.documents):
            raise ValueError("context total_bytes does not match documents")
        return self

    def as_prompt(self) -> str:
        return "\n\n".join(
            f"--- BEGIN {document.path} ---\n{document.content}\n--- END {document.path} ---"
            for document in self.documents
        )


def _validate_limits(max_files: int, max_file_bytes: int, max_total_bytes: int) -> None:
    values = (max_files, max_file_bytes, max_total_bytes)
    if any(isinstance(value, bool) or not isinstance(value, int) or value < 1 for value in values):
        raise ContextBoundaryError("context limits must be positive integers")
    if max_files > 32 or max_file_bytes > 100_000 or max_total_bytes > 500_000:
        raise ContextBoundaryError("context limits exceed hard safety ceilings")


def build_context_bundle(
    workspace: Path,
    relative_paths: tuple[str, ...],
    *,
    workspace_fingerprint: str,
    max_files: int = 16,
    max_file_bytes: int = 20_000,
    max_total_bytes: int = 80_000,
) -> ContextBundle:
    """Read a deterministic allowlist without following symlinks or protected names."""

    _validate_limits(max_files, max_file_bytes, max_total_bytes)
    if not relative_paths or len(relative_paths) > max_files:
        raise ContextBoundaryError("context file count is outside configured bounds")
    if len(relative_paths) != len(set(relative_paths)):
        raise ContextBoundaryError("context paths must not contain duplicates")
    if workspace.is_symlink() or not workspace.is_dir():
        raise ContextBoundaryError("workspace must be a real directory")
    try:
        root = workspace.resolve(strict=True)
    except OSError as error:
        raise ContextBoundaryError(
            f"workspace cannot be resolved: {type(error).__name__}"
        ) from None

    documents: list[ContextDocument] = []
    total_bytes = 0
    for relative_text in sorted(relative_paths):
        try:
            canonical = RELATIVE_PATH_ADAPTER.validate_python(relative_text)
        except ValueError:
            raise ContextBoundaryError("context path is not a safe relative POSIX path") from None
        relative = PurePosixPath(canonical)
        if any(part in PROTECTED_NAMES for part in relative.parts):
            raise ContextBoundaryError(f"context path is protected: {canonical}")

        candidate = root
        for part in relative.parts:
            candidate /= part
            if candidate.is_symlink():
                raise ContextBoundaryError(f"context path contains a symlink: {canonical}")
        try:
            before = candidate.stat()
            resolved = candidate.resolve(strict=True)
        except OSError as error:
            raise ContextBoundaryError(
                f"context file cannot be resolved: {canonical} ({type(error).__name__})"
            ) from None
        if not resolved.is_relative_to(root) or not stat.S_ISREG(before.st_mode):
            raise ContextBoundaryError(f"context path is not a workspace file: {canonical}")
        if before.st_size > max_file_bytes:
            raise ContextBoundaryError(f"context file exceeds per-file limit: {canonical}")
        total_bytes += before.st_size
        if total_bytes > max_total_bytes:
            raise ContextBoundaryError("context exceeds total byte limit")
        try:
            contents = candidate.read_bytes()
            after = candidate.stat()
            text = contents.decode("utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise ContextBoundaryError(
                f"context file is not stable UTF-8: {canonical} ({type(error).__name__})"
            ) from None
        identity_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        identity_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        if identity_before != identity_after or len(contents) != before.st_size:
            raise ContextBoundaryError(f"context file changed while reading: {canonical}")
        documents.append(
            ContextDocument(
                path=canonical,
                content=text,
                size_bytes=len(contents),
                sha256=sha256(contents).hexdigest(),
            )
        )

    return ContextBundle(
        workspace_fingerprint=workspace_fingerprint,
        documents=tuple(documents),
        total_bytes=total_bytes,
    )


def build_scenario_context(
    repository_root: Path,
    scenario_id: str,
    *,
    relative_paths: tuple[str, ...] = (".scenario/manifest.json", "TASK.md"),
    requested_state_root: Path | None = None,
) -> ContextBundle:
    """Verify the managed disposable workspace before reading any prompt context."""

    manifest = load_manifest(repository_root, scenario_id)
    status = verify_workspace(
        repository_root,
        manifest,
        requested_state_root=requested_state_root,
    )
    return build_context_bundle(
        Path(status["workspace"]),
        relative_paths,
        workspace_fingerprint=status["actual_fingerprint"],
    )
