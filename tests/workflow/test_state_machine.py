from itertools import product

import pytest

from contracts import (
    ImplementationStatus,
    QADecision,
    ReviewDecision,
    ValidationDecision,
)
from orchestrator import (
    ALLOWED_TRANSITIONS,
    ArtifactGateError,
    BudgetCharge,
    BudgetExceededError,
    BudgetState,
    BudgetUsage,
    IllegalTransitionError,
    Stage,
    TransitionCommand,
    WorkflowState,
    append_transition,
    apply_transition,
    initial_state,
    verify_event_chain,
)
from tests.workflow.factories import (
    TASK_ID,
    analysis_report,
    at,
    budget_limits,
    implementation_result,
    qa_report,
    review_report,
    specification,
    task_request,
    validation_result,
)


def _command(
    command_id: str,
    target: Stage,
    second: int,
    *,
    actor: str = "workflow",
    artifact=None,
    charge: BudgetCharge | None = None,
    reason: str | None = None,
) -> TransitionCommand:
    if target is Stage.REWORK and charge is None:
        charge = BudgetCharge(rework_attempts=1)
    if target in {Stage.REWORK, Stage.BLOCKED, Stage.FAILED} and reason is None:
        reason = "deterministic gate decision"
    return TransitionCommand(
        command_id=command_id,
        task_id=TASK_ID,
        actor_id=actor,
        target_stage=target,
        occurred_at=at(second),
        artifact=artifact,
        charge=charge or BudgetCharge(),
        reason=reason,
    )


def _state_at(stage: Stage, *, rework_used: int = 0, rework_limit: int = 2) -> WorkflowState:
    author = None
    if stage in {
        Stage.IMPLEMENTED,
        Stage.VALIDATING,
        Stage.VALIDATED,
        Stage.QA,
        Stage.QA_PASSED,
        Stage.REVIEW,
        Stage.REWORK,
        Stage.DONE,
    }:
        author = "data-engineer"
    return WorkflowState(
        workflow_id="workflow-1",
        correlation_id="correlation-1",
        task_id=TASK_ID,
        stage=stage,
        revision=0,
        budgets=BudgetState(
            limits=budget_limits(rework_attempts=rework_limit),
            used=BudgetUsage(rework_attempts=rework_used),
        ),
        artifact_ids=("artifact-task-request",),
        implementation_author_id=author,
        terminal_reason="terminal fixture" if stage in {Stage.BLOCKED, Stage.FAILED} else None,
    )


def test_happy_path_reaches_done_with_verified_event_chain() -> None:
    task = task_request()
    state = initial_state(
        task,
        workflow_id="workflow-1",
        correlation_id="correlation-1",
        limits=budget_limits(),
    )
    initial = state
    events = ()
    spec = specification()
    analysis = analysis_report()
    implementation = implementation_result()
    validation = validation_result()
    qa = qa_report()
    review = review_report()
    commands = (
        _command("command-01", Stage.SPECIFYING, 1),
        _command("command-02", Stage.SPEC_READY, 2, actor="pm", artifact=spec),
        _command("command-03", Stage.ANALYZING, 3),
        _command("command-04", Stage.ANALYSIS_READY, 4, actor="analyst", artifact=analysis),
        _command("command-05", Stage.IMPLEMENTING, 5),
        _command(
            "command-06",
            Stage.IMPLEMENTED,
            6,
            actor="data-engineer",
            artifact=implementation,
            charge=BudgetCharge(tool_calls=8, model_tokens=1_200, wall_time_seconds=90),
        ),
        _command("command-07", Stage.VALIDATING, 7),
        _command("command-08", Stage.VALIDATED, 8, actor="validator", artifact=validation),
        _command("command-09", Stage.QA, 9),
        _command("command-10", Stage.QA_PASSED, 10, actor="qa", artifact=qa),
        _command("command-11", Stage.REVIEW, 11),
        _command("command-12", Stage.DONE, 12, actor="reviewer", artifact=review),
    )

    for command in commands:
        state, events = append_transition(state, command, events)

    verify_event_chain(events, expected_state=state)
    assert initial.stage is Stage.CREATED
    assert initial.revision == 0
    assert state.stage is Stage.DONE
    assert state.revision == 12
    assert state.implementation_author_id == "data-engineer"
    assert state.budgets.used.tool_calls == 8
    assert len(events) == 12
    assert events[0].previous_hash is None
    assert events[-1].state_hash


def test_every_edge_missing_from_transition_table_is_rejected() -> None:
    checked = 0
    for source, target in product(Stage, repeat=2):
        if target in ALLOWED_TRANSITIONS[source]:
            continue
        state = _state_at(source)
        command = _command(f"command-{source.value}-{target.value}", target, 1)
        with pytest.raises(IllegalTransitionError):
            apply_transition(state, command)
        checked += 1

    assert checked == sum(
        1
        for source, target in product(Stage, repeat=2)
        if target not in ALLOWED_TRANSITIONS[source]
    )


def test_role_artifact_cannot_skip_a_gate_or_claim_wrong_decision() -> None:
    implementing = _state_at(Stage.IMPLEMENTING)
    with pytest.raises(IllegalTransitionError):
        apply_transition(
            implementing,
            _command(
                "command-skip",
                Stage.DONE,
                6,
                actor="data-engineer",
                artifact=implementation_result(),
            ),
        )

    validating = _state_at(Stage.VALIDATING)
    with pytest.raises(ArtifactGateError, match="passing"):
        apply_transition(
            validating,
            _command(
                "command-wrong-validation",
                Stage.VALIDATED,
                8,
                actor="validator",
                artifact=validation_result(decision=ValidationDecision.FAIL),
            ),
        )


def test_cross_task_or_wrong_actor_artifact_is_rejected() -> None:
    state = _state_at(Stage.SPECIFYING)
    wrong_task = specification().model_copy(update={"task_id": "TASK-OTHER"})
    with pytest.raises(ArtifactGateError, match="task"):
        apply_transition(
            state,
            _command("command-cross-task", Stage.SPEC_READY, 2, actor="pm", artifact=wrong_task),
        )

    with pytest.raises(ArtifactGateError, match="producer"):
        apply_transition(
            state,
            _command(
                "command-wrong-actor",
                Stage.SPEC_READY,
                2,
                actor="reviewer",
                artifact=specification(),
            ),
        )


def test_rework_consumes_one_attempt_and_exhaustion_fails_closed() -> None:
    report = validation_result(decision=ValidationDecision.FAIL, artifact_id="validation-fail-1")
    state = _state_at(Stage.VALIDATING, rework_used=0, rework_limit=1)
    first = apply_transition(
        state,
        _command(
            "command-rework-1",
            Stage.REWORK,
            8,
            actor="validator",
            artifact=report,
        ),
    )

    assert first.stage is Stage.REWORK
    assert first.budgets.used.rework_attempts == 1

    exhausted = _state_at(Stage.VALIDATING, rework_used=1, rework_limit=1)
    second_report = validation_result(
        decision=ValidationDecision.FAIL, artifact_id="validation-fail-2"
    )
    failed = apply_transition(
        exhausted,
        _command(
            "command-rework-2",
            Stage.REWORK,
            9,
            actor="validator",
            artifact=second_report,
        ),
    )

    assert failed.stage is Stage.FAILED
    assert failed.budgets.used.rework_attempts == 1
    assert failed.budgets.remaining.rework_attempts == 0
    assert failed.terminal_reason == "rework budget exhausted: deterministic gate decision"

    initial = _state_at(Stage.VALIDATING, rework_used=1, rework_limit=1)
    _, events = append_transition(
        initial,
        _command(
            "command-rework-event",
            Stage.REWORK,
            9,
            actor="validator",
            artifact=second_report,
        ),
        (),
    )
    assert events[0].requested_stage is Stage.REWORK
    assert events[0].to_stage is Stage.FAILED
    assert events[0].charge.rework_attempts == 0


def test_resource_budget_cannot_underflow_or_mutate_original_state() -> None:
    state = _state_at(Stage.CREATED)
    original_budget = state.budgets
    command = _command(
        "command-over-budget",
        Stage.SPECIFYING,
        1,
        charge=BudgetCharge(tool_calls=101),
    )

    with pytest.raises(BudgetExceededError, match="tool_calls"):
        apply_transition(state, command)

    assert state.budgets == original_budget
    assert state.budgets.used.tool_calls == 0


@pytest.mark.parametrize(
    ("stage", "artifact", "actor", "target"),
    [
        (
            Stage.IMPLEMENTING,
            implementation_result(status=ImplementationStatus.BLOCKED),
            "data-engineer",
            Stage.BLOCKED,
        ),
        (
            Stage.IMPLEMENTING,
            implementation_result(status=ImplementationStatus.FAILED),
            "data-engineer",
            Stage.FAILED,
        ),
        (Stage.QA, qa_report(decision=QADecision.BLOCKED), "qa", Stage.BLOCKED),
        (
            Stage.REVIEW,
            review_report(decision=ReviewDecision.BLOCKED),
            "reviewer",
            Stage.BLOCKED,
        ),
    ],
)
def test_matching_blocked_and_failed_artifacts_reach_terminal_state(
    stage: Stage, artifact, actor: str, target: Stage
) -> None:
    result = apply_transition(
        _state_at(stage),
        _command("command-terminal", target, 12, actor=actor, artifact=artifact),
    )

    assert result.stage is target
    assert result.terminal_reason == "deterministic gate decision"
