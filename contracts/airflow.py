"""Contracts for out-of-band approval of one local Airflow trigger."""

from __future__ import annotations

from datetime import timedelta
from typing import Self

from pydantic import model_validator

from contracts.common import Identifier, UtcDateTime, VersionedModel
from contracts.tools import AirflowObjectId, IdempotencyKey


class AirflowTriggerApproval(VersionedModel):
    approval_id: Identifier
    task_id: Identifier
    dag_id: AirflowObjectId
    idempotency_key: IdempotencyKey
    approved_by: Identifier
    created_at: UtcDateTime
    expires_at: UtcDateTime
    consumed_at: UtcDateTime | None = None
    run_id: AirflowObjectId | None = None

    @model_validator(mode="after")
    def validate_lifecycle(self) -> Self:
        if self.expires_at <= self.created_at:
            raise ValueError("approval expiry must follow creation")
        if self.expires_at - self.created_at > timedelta(minutes=15):
            raise ValueError("approval lifetime exceeds 15 minutes")
        if (self.consumed_at is None) != (self.run_id is None):
            raise ValueError("approval consumption timestamp and run ID must appear together")
        if self.consumed_at is not None and self.consumed_at < self.created_at:
            raise ValueError("approval cannot be consumed before creation")
        return self
