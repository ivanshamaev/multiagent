"""Hardened durable receipts for idempotent role executor replay."""

from __future__ import annotations

import json
import os
import re
import stat
import uuid
from hashlib import sha256
from pathlib import Path

from pydantic import Field

from contracts.common import FrozenModel, Identifier, NonNegativeInt, Sha256

OPERATION_ID = re.compile(r"[0-9a-f]{64}")
MAX_RECEIPT_BYTES = 6_000_000
ROLE_RECEIPT_PROTOCOL = "role-receipt-v1"


class RoleReceiptError(RuntimeError):
    """Receipt storage or integrity validation failed closed."""


class RoleReceipt(FrozenModel):
    operation_id: Sha256
    workflow_id: Identifier
    executor_id: Identifier
    input_revision: NonNegativeInt
    input_sha256: Sha256
    output_sha256: Sha256
    output: str = Field(min_length=1, max_length=5_000_000)


def role_operation_id(
    *, workflow_id: str, executor_id: str, input_revision: int, input_payload: str
) -> str:
    input_hash = sha256(input_payload.encode("utf-8")).hexdigest()
    material = (
        f"{ROLE_RECEIPT_PROTOCOL}\0{workflow_id}\0{executor_id}\0{input_revision}\0{input_hash}"
    )
    return sha256(material.encode("utf-8")).hexdigest()


class SecureRoleReceiptStore:
    """Contained, owner-only and create-only JSON receipt store."""

    def __init__(self, repository_root: Path, storage_path: Path | None = None) -> None:
        if repository_root.is_symlink():
            raise RoleReceiptError("repository root must not be a symlink")
        self.repository_root = repository_root.resolve(strict=True)
        requested = storage_path or self.repository_root / ".scenario-state/role-receipts"
        if not requested.is_absolute():
            raise RoleReceiptError("receipt storage path must be absolute")
        try:
            relative = requested.relative_to(self.repository_root)
        except ValueError:
            raise RoleReceiptError("receipt storage escaped the repository") from None
        current = self.repository_root
        for component in relative.parts:
            current /= component
            if current.is_symlink():
                raise RoleReceiptError("receipt storage must not contain symlinks")
        resolved = requested.resolve(strict=False)
        if not resolved.is_relative_to(self.repository_root):
            raise RoleReceiptError("receipt storage escaped the repository")
        existed = resolved.exists()
        resolved.mkdir(parents=True, exist_ok=True, mode=0o700)
        if existed and stat.S_IMODE(resolved.stat().st_mode) != 0o700:
            raise RoleReceiptError("receipt storage must have mode 0700")
        resolved.chmod(0o700)
        self.storage_path = resolved

    @staticmethod
    def _validate_id(operation_id: str) -> None:
        if OPERATION_ID.fullmatch(operation_id) is None:
            raise RoleReceiptError("operation ID is invalid")

    def _path(self, operation_id: str) -> Path:
        self._validate_id(operation_id)
        return self.storage_path / f"{operation_id}.json"

    def _read(self, operation_id: str) -> RoleReceipt:
        path = self._path(operation_id)
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            raise RoleReceiptError("receipt does not exist") from None
        if path.is_symlink() or not stat.S_ISREG(metadata.st_mode):
            raise RoleReceiptError("receipt must be a regular non-symlink file")
        if stat.S_IMODE(metadata.st_mode) != 0o600:
            raise RoleReceiptError("receipt must have mode 0600")
        if not 1 <= metadata.st_size <= MAX_RECEIPT_BYTES:
            raise RoleReceiptError("receipt size is invalid")
        try:
            receipt = RoleReceipt.model_validate_json(path.read_bytes(), strict=True)
        except (OSError, ValueError) as error:
            raise RoleReceiptError("receipt content is invalid") from error
        if receipt.operation_id != operation_id:
            raise RoleReceiptError("receipt identity is invalid")
        if sha256(receipt.output.encode("utf-8")).hexdigest() != receipt.output_sha256:
            raise RoleReceiptError("receipt output hash is invalid")
        return receipt

    def get(self, operation_id: str) -> RoleReceipt | None:
        path = self._path(operation_id)
        if not path.exists():
            if path.is_symlink():
                raise RoleReceiptError("receipt target must not be a symlink")
            return None
        return self._read(operation_id)

    def save(self, receipt: RoleReceipt) -> None:
        target = self._path(receipt.operation_id)
        existing = self.get(receipt.operation_id)
        if existing is not None:
            if existing != receipt:
                raise RoleReceiptError("receipt collision detected")
            return
        payload = json.dumps(
            receipt.model_dump(mode="json"),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        if len(payload) > MAX_RECEIPT_BYTES:
            raise RoleReceiptError("receipt exceeds the size limit")
        temporary = self.storage_path / f".{uuid.uuid4().hex}.tmp"
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                os.link(temporary, target, follow_symlinks=False)
            except FileExistsError:
                existing = self._read(receipt.operation_id)
                if existing != receipt:
                    raise RoleReceiptError("receipt collision detected") from None
            directory = os.open(self.storage_path, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            temporary.unlink(missing_ok=True)
