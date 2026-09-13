"""Atomic, short-lived approvals for one local Airflow trigger."""

from __future__ import annotations

import fcntl
import json
import os
import secrets
import stat
import tempfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from pydantic import TypeAdapter, ValidationError

from contracts import AirflowTriggerApproval
from contracts.common import Identifier

MAX_APPROVAL_BYTES = 16_384


class AirflowApprovalError(RuntimeError):
    """A safely reportable approval-boundary failure."""


@dataclass
class AirflowApprovalClaim:
    approval: AirflowTriggerApproval
    _store: AirflowApprovalStore
    _consumed: bool = False

    def consume(self, run_id: str) -> None:
        if self._consumed:
            raise AirflowApprovalError("Airflow trigger approval was already consumed")
        now = self._store.now()
        payload = self.approval.model_dump(mode="json")
        payload.update(consumed_at=now.isoformat(), run_id=run_id)
        try:
            consumed = AirflowTriggerApproval.model_validate(payload)
        except ValidationError:
            raise AirflowApprovalError("Airflow trigger approval consumption is invalid") from None
        self._store._replace(consumed)
        self._consumed = True


class AirflowApprovalStore:
    """Create and consume approval records under one repository-local state root."""

    def __init__(
        self,
        repository_root: Path,
        approval_root: Path | None = None,
        *,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        try:
            repository = repository_root.resolve(strict=True)
        except OSError as error:
            raise AirflowApprovalError(
                f"repository root cannot be resolved ({type(error).__name__})"
            ) from None
        root = approval_root or repository / ".scenario-state/airflow-trigger-approvals"
        root = root if root.is_absolute() else repository / root
        if root.is_symlink():
            raise AirflowApprovalError("Airflow approval root must not be a symlink")
        try:
            root.mkdir(mode=0o700, parents=True, exist_ok=True)
            root = root.resolve(strict=True)
        except OSError as error:
            raise AirflowApprovalError(
                f"Airflow approval root cannot be prepared ({type(error).__name__})"
            ) from None
        if not root.is_dir() or not root.is_relative_to(repository):
            raise AirflowApprovalError("Airflow approval root must stay inside the repository")
        os.chmod(root, 0o700)
        self._root = root
        self._clock = clock

    def now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None or value.utcoffset() != timedelta(0):
            raise AirflowApprovalError("approval clock must return UTC")
        return value

    def create(
        self,
        *,
        task_id: str,
        dag_id: str,
        idempotency_key: str,
        approved_by: str,
        ttl_seconds: int = 300,
    ) -> AirflowTriggerApproval:
        if not 30 <= ttl_seconds <= 900:
            raise AirflowApprovalError("approval TTL must be between 30 and 900 seconds")
        now = self.now()
        try:
            approval = AirflowTriggerApproval(
                approval_id=f"airflow-approval-{secrets.token_hex(12)}",
                task_id=task_id,
                dag_id=dag_id,
                idempotency_key=idempotency_key,
                approved_by=approved_by,
                created_at=now,
                expires_at=now + timedelta(seconds=ttl_seconds),
            )
        except ValidationError:
            raise AirflowApprovalError("Airflow trigger approval fields are invalid") from None
        with self._lock():
            target = self._path(approval.approval_id)
            try:
                descriptor = os.open(
                    target,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                    0o600,
                )
                with os.fdopen(descriptor, "wb") as stream:
                    stream.write(self._encode(approval))
                    stream.flush()
                    os.fsync(stream.fileno())
            except OSError as error:
                raise AirflowApprovalError(
                    f"Airflow trigger approval cannot be created ({type(error).__name__})"
                ) from None
        return approval

    @contextmanager
    def claim(
        self,
        *,
        approval_id: str,
        task_id: str,
        dag_id: str,
        idempotency_key: str,
    ) -> Iterator[AirflowApprovalClaim]:
        with self._lock():
            approval = self._read(approval_id)
            if approval.consumed_at is not None:
                raise AirflowApprovalError("Airflow trigger approval was already consumed")
            if self.now() >= approval.expires_at:
                raise AirflowApprovalError("Airflow trigger approval expired")
            if (
                approval.task_id != task_id
                or approval.dag_id != dag_id
                or approval.idempotency_key != idempotency_key
            ):
                raise AirflowApprovalError("Airflow trigger approval does not match the request")
            yield AirflowApprovalClaim(approval=approval, _store=self)

    @contextmanager
    def _lock(self) -> Iterator[None]:
        path = self._root / ".approval.lock"
        descriptor = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            metadata = os.fstat(descriptor)
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_mode & 0o077:
                raise AirflowApprovalError("Airflow approval lock is unsafe")
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            yield
        finally:
            os.close(descriptor)

    def _read(self, approval_id: str) -> AirflowTriggerApproval:
        path = self._path(approval_id)
        try:
            descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(descriptor, "rb") as stream:
                metadata = os.fstat(stream.fileno())
                if (
                    not stat.S_ISREG(metadata.st_mode)
                    or metadata.st_mode & 0o077
                    or metadata.st_size > MAX_APPROVAL_BYTES
                ):
                    raise AirflowApprovalError("Airflow trigger approval file is unsafe")
                payload = stream.read(MAX_APPROVAL_BYTES + 1)
        except FileNotFoundError:
            raise AirflowApprovalError("Airflow trigger approval does not exist") from None
        except OSError as error:
            raise AirflowApprovalError(
                f"Airflow trigger approval cannot be read ({type(error).__name__})"
            ) from None
        try:
            return AirflowTriggerApproval.model_validate_json(payload)
        except ValidationError:
            raise AirflowApprovalError("Airflow trigger approval is invalid") from None

    def _replace(self, approval: AirflowTriggerApproval) -> None:
        target = self._path(approval.approval_id)
        descriptor, temporary_text = tempfile.mkstemp(prefix=".approval-", dir=self._root)
        temporary = Path(temporary_text)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(self._encode(approval))
                stream.flush()
                os.fsync(stream.fileno())
                os.fchmod(stream.fileno(), 0o600)
            os.replace(temporary, target)
        except OSError as error:
            raise AirflowApprovalError(
                f"Airflow trigger approval cannot be consumed ({type(error).__name__})"
            ) from None
        finally:
            if temporary.exists():
                temporary.unlink()

    def _path(self, approval_id: str) -> Path:
        try:
            safe_id = TypeAdapter(Identifier).validate_python(approval_id)
        except ValidationError:
            raise AirflowApprovalError("Airflow trigger approval ID is invalid") from None
        return self._root / f"{safe_id}.json"

    @staticmethod
    def _encode(approval: AirflowTriggerApproval) -> bytes:
        return json.dumps(
            approval.model_dump(mode="json"),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
