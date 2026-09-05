"""Canonical append-only event envelope for accepted workflow transitions."""

from __future__ import annotations

import hashlib
import json
from typing import Literal, Self

from pydantic import model_validator

from contracts.common import (
    Identifier,
    NonEmptyText,
    NonNegativeInt,
    Sha256,
    UtcDateTime,
    VersionedModel,
)
from orchestrator.errors import EventChainError
from orchestrator.state import BudgetCharge, Stage, WorkflowState
from orchestrator.transitions import TransitionCommand, apply_transition


class WorkflowEvent(VersionedModel):
    event_type: Literal["workflow_transition"] = "workflow_transition"
    event_id: Identifier
    sequence: NonNegativeInt
    state_revision: NonNegativeInt
    workflow_id: Identifier
    task_id: Identifier
    correlation_id: Identifier
    actor_id: Identifier
    occurred_at: UtcDateTime
    from_stage: Stage
    requested_stage: Stage
    to_stage: Stage
    artifact_id: Identifier | None = None
    charge: BudgetCharge
    reason: NonEmptyText | None = None
    previous_hash: Sha256 | None
    state_hash: Sha256
    event_hash: Sha256

    @model_validator(mode="after")
    def validate_position(self) -> Self:
        if (self.sequence == 0) != (self.previous_hash is None):
            raise ValueError("only sequence zero may omit previous_hash")
        if self.state_revision != self.sequence + 1:
            raise ValueError("state_revision must equal sequence + 1")
        return self


def _canonical_hash(value: VersionedModel, *, exclude: set[str] | None = None) -> str:
    payload = value.model_dump(mode="json", exclude=exclude or set())
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def state_hash(state: WorkflowState) -> str:
    return _canonical_hash(state)


def event_hash(event: WorkflowEvent) -> str:
    return _canonical_hash(event, exclude={"event_hash"})


def _create_event(
    before: WorkflowState,
    after: WorkflowState,
    command: TransitionCommand,
    previous: WorkflowEvent | None,
) -> WorkflowEvent:
    applied_charge = BudgetCharge(
        **{
            field: getattr(after.budgets.used, field) - getattr(before.budgets.used, field)
            for field in BudgetCharge.model_fields
        }
    )
    provisional = WorkflowEvent(
        event_id=command.command_id,
        sequence=0 if previous is None else previous.sequence + 1,
        state_revision=after.revision,
        workflow_id=after.workflow_id,
        task_id=after.task_id,
        correlation_id=after.correlation_id,
        actor_id=command.actor_id,
        occurred_at=command.occurred_at,
        from_stage=before.stage,
        requested_stage=command.target_stage,
        to_stage=after.stage,
        artifact_id=None if command.artifact is None else command.artifact.artifact_id,
        charge=applied_charge,
        reason=after.terminal_reason or command.reason,
        previous_hash=None if previous is None else previous.event_hash,
        state_hash=state_hash(after),
        event_hash="0" * 64,
    )
    return WorkflowEvent.model_validate(
        {**provisional.model_dump(), "event_hash": event_hash(provisional)}
    )


def verify_event_chain(
    events: tuple[WorkflowEvent, ...], *, expected_state: WorkflowState | None = None
) -> None:
    """Reject mutation, reorder, replay, truncation against expected state, and mixed runs."""

    event_ids: set[str] = set()
    previous: WorkflowEvent | None = None
    for index, event in enumerate(events):
        if event.sequence != index or event.state_revision != index + 1:
            raise EventChainError("event sequence or revision is not contiguous")
        if event.event_id in event_ids:
            raise EventChainError("event replay detected")
        event_ids.add(event.event_id)
        expected_previous = None if previous is None else previous.event_hash
        if event.previous_hash != expected_previous:
            raise EventChainError("event previous_hash mismatch")
        if event.event_hash != event_hash(event):
            raise EventChainError("event content hash mismatch")
        if previous is not None:
            if event.from_stage is not previous.to_stage:
                raise EventChainError("event stages are not contiguous")
            if (
                event.workflow_id != previous.workflow_id
                or event.task_id != previous.task_id
                or event.correlation_id != previous.correlation_id
            ):
                raise EventChainError("event identity changed inside the chain")
            if event.occurred_at < previous.occurred_at:
                raise EventChainError("event timestamps are not monotonic")
        previous = event

    if expected_state is None:
        return
    if not events and expected_state.revision != 0:
        raise EventChainError("non-initial state requires events")
    if events:
        last = events[-1]
        if (
            last.to_stage is not expected_state.stage
            or last.state_revision != expected_state.revision
            or last.state_hash != state_hash(expected_state)
        ):
            raise EventChainError("event chain does not represent the expected state")


def append_transition(
    state: WorkflowState,
    command: TransitionCommand,
    events: tuple[WorkflowEvent, ...],
) -> tuple[WorkflowState, tuple[WorkflowEvent, ...]]:
    """Atomically reduce state and append one verifiable event in memory."""

    verify_event_chain(events, expected_state=state)
    next_state = apply_transition(state, command)
    event = _create_event(state, next_state, command, events[-1] if events else None)
    next_events = (*events, event)
    verify_event_chain(next_events, expected_state=next_state)
    return next_state, next_events
