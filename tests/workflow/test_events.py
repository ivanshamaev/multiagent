import pytest
from pydantic import ValidationError

from orchestrator import (
    BudgetCharge,
    EventChainError,
    Stage,
    TransitionCommand,
    WorkflowEvent,
    append_transition,
    initial_state,
    verify_event_chain,
)
from tests.workflow.factories import TASK_ID, at, budget_limits, specification, task_request


def _two_event_chain():
    state = initial_state(
        task_request(),
        workflow_id="workflow-events",
        correlation_id="correlation-events",
        limits=budget_limits(),
    )
    events = ()
    first = TransitionCommand(
        command_id="event-command-1",
        task_id=TASK_ID,
        actor_id="workflow",
        target_stage=Stage.SPECIFYING,
        occurred_at=at(1),
    )
    state, events = append_transition(state, first, events)
    spec = specification()
    second = TransitionCommand(
        command_id="event-command-2",
        task_id=TASK_ID,
        actor_id="pm",
        target_stage=Stage.SPEC_READY,
        occurred_at=at(2),
        artifact=spec,
        charge=BudgetCharge(model_tokens=50),
    )
    state, events = append_transition(state, second, events)
    return state, events


def test_events_round_trip_and_chain_remain_valid() -> None:
    state, events = _two_event_chain()
    restored = tuple(WorkflowEvent.model_validate_json(item.model_dump_json()) for item in events)

    verify_event_chain(restored, expected_state=state)
    assert restored == events
    assert restored[1].previous_hash == restored[0].event_hash


def test_event_is_frozen() -> None:
    _, events = _two_event_chain()

    with pytest.raises(ValidationError, match="frozen"):
        events[0].actor_id = "attacker"  # type: ignore[misc]


def test_mutation_reorder_and_replay_are_detected() -> None:
    state, events = _two_event_chain()
    forged = events[0].model_copy(update={"actor_id": "attacker"})
    with pytest.raises(EventChainError, match="content hash"):
        verify_event_chain((forged, events[1]), expected_state=state)
    with pytest.raises(EventChainError, match="sequence"):
        verify_event_chain(tuple(reversed(events)), expected_state=state)
    replayed = (*events, events[1])
    with pytest.raises(EventChainError, match=r"sequence|replay"):
        verify_event_chain(replayed)


def test_truncation_is_detected_against_current_state() -> None:
    state, events = _two_event_chain()

    with pytest.raises(EventChainError, match="expected state"):
        verify_event_chain(events[:-1], expected_state=state)


def test_append_rejects_events_from_another_state() -> None:
    state, events = _two_event_chain()
    other = state.model_copy(update={"correlation_id": "different-correlation"})
    command = TransitionCommand(
        command_id="event-command-3",
        task_id=TASK_ID,
        actor_id="workflow",
        target_stage=Stage.ANALYZING,
        occurred_at=at(3),
    )

    with pytest.raises(EventChainError, match="expected state"):
        append_transition(other, command, events)
