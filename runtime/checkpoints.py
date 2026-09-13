"""Hardened local adapter for Microsoft Agent Framework checkpoints."""

from __future__ import annotations

import re
import stat
from datetime import datetime
from pathlib import Path

from agent_framework import FileCheckpointStorage, WorkflowCheckpoint
from agent_framework.exceptions import WorkflowCheckpointException

CHECKPOINT_ID = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"
)
MAX_CHECKPOINT_BYTES = 10_000_000


class SecureCheckpointStorage:
    """Contain and permission-check MAF's restricted file checkpoint backend."""

    def __init__(self, repository_root: Path, storage_path: Path | None = None) -> None:
        if repository_root.is_symlink():
            raise WorkflowCheckpointException("repository root must not be a symlink")
        self.repository_root = repository_root.resolve(strict=True)
        requested = storage_path or self.repository_root / ".scenario-state/checkpoints"
        if not requested.is_absolute():
            raise WorkflowCheckpointException("checkpoint storage path must be absolute")
        try:
            relative = requested.relative_to(self.repository_root)
        except ValueError:
            raise WorkflowCheckpointException("checkpoint storage escaped the repository") from None
        current = self.repository_root
        for component in relative.parts:
            current /= component
            if current.is_symlink():
                raise WorkflowCheckpointException("checkpoint storage must not contain symlinks")
        resolved = requested.resolve(strict=False)
        if not resolved.is_relative_to(self.repository_root):
            raise WorkflowCheckpointException("checkpoint storage escaped the repository")
        existed = resolved.exists()
        resolved.mkdir(parents=True, exist_ok=True, mode=0o700)
        if existed and stat.S_IMODE(resolved.stat().st_mode) != 0o700:
            raise WorkflowCheckpointException("checkpoint storage must have mode 0700")
        resolved.chmod(0o700)
        self.storage_path = resolved
        self._delegate = FileCheckpointStorage(resolved)

    @staticmethod
    def _validate_id(checkpoint_id: str) -> None:
        if CHECKPOINT_ID.fullmatch(checkpoint_id) is None:
            raise WorkflowCheckpointException("checkpoint ID is invalid")

    def _path(self, checkpoint_id: str) -> Path:
        self._validate_id(checkpoint_id)
        return self.storage_path / f"{checkpoint_id}.json"

    def _validate_file(self, checkpoint_id: str) -> Path:
        path = self._path(checkpoint_id)
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            raise WorkflowCheckpointException("checkpoint does not exist") from None
        if path.is_symlink() or not stat.S_ISREG(metadata.st_mode):
            raise WorkflowCheckpointException("checkpoint must be a regular non-symlink file")
        if stat.S_IMODE(metadata.st_mode) != 0o600:
            raise WorkflowCheckpointException("checkpoint must have mode 0600")
        if metadata.st_size > MAX_CHECKPOINT_BYTES:
            raise WorkflowCheckpointException("checkpoint exceeds the size limit")
        return path

    async def save(self, checkpoint: WorkflowCheckpoint) -> str:
        self._validate_id(checkpoint.checkpoint_id)
        target = self._path(checkpoint.checkpoint_id)
        if target.is_symlink():
            raise WorkflowCheckpointException("checkpoint target must not be a symlink")
        if target.exists():
            raise WorkflowCheckpointException("checkpoint already exists")
        checkpoint_id = await self._delegate.save(checkpoint)
        target.chmod(0o600)
        self._validate_file(checkpoint_id)
        return checkpoint_id

    async def load(self, checkpoint_id: str) -> WorkflowCheckpoint:
        self._validate_file(checkpoint_id)
        return await self._delegate.load(checkpoint_id)

    async def list_checkpoints(self, *, workflow_name: str) -> list[WorkflowCheckpoint]:
        checkpoints: list[WorkflowCheckpoint] = []
        for path in sorted(self.storage_path.iterdir()):
            if path.name.endswith(".json.tmp"):
                continue
            if path.suffix != ".json":
                raise WorkflowCheckpointException("unexpected checkpoint storage entry")
            checkpoints.append(await self.load(path.stem))
        return [item for item in checkpoints if item.workflow_name == workflow_name]

    async def list_checkpoint_ids(self, *, workflow_name: str) -> list[str]:
        return [
            item.checkpoint_id for item in await self.list_checkpoints(workflow_name=workflow_name)
        ]

    async def get_latest(self, *, workflow_name: str) -> WorkflowCheckpoint | None:
        checkpoints = await self.list_checkpoints(workflow_name=workflow_name)
        if not checkpoints:
            return None
        return max(checkpoints, key=lambda item: datetime.fromisoformat(item.timestamp))

    async def delete(self, checkpoint_id: str) -> bool:
        self._validate_id(checkpoint_id)
        if not self._path(checkpoint_id).exists():
            return False
        self._validate_file(checkpoint_id)
        return await self._delegate.delete(checkpoint_id)
