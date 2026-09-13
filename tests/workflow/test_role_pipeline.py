import asyncio
from dataclasses import replace
from hashlib import sha256
from pathlib import Path

import pytest

from contracts import (
    ImplementationStatus,
    PMRequirementsHandoff,
    QADecision,
    ReviewDecision,
    SpecificationDecision,
    ValidationDecision,
)
from orchestrator import (
    BudgetCharge,
    Stage,
    TransitionCommand,
    append_transition,
    initial_state,
)
from runtime.analyst import AnalystRunRequest
from runtime.checkpoints import SecureCheckpointStorage
from runtime.context import ContextBundle, ContextDocument
from runtime.role_pipeline import (
    PMExecutor,
    RoleBoundaryError,
    RolePipelineHandlers,
    RolePipelineSnapshot,
    build_role_pipeline,
    decode_role_snapshot,
    encode_role_snapshot,
    initial_role_message,
)
from runtime.role_receipts import SecureRoleReceiptStore
from tests.workflow.factories import (
    analysis_report,
    at,
    budget_limits,
    implementation_result,
    qa_report,
    requirements_analysis_report,
    review_report,
    specification,
    task_request,
    validation_result,
)


def _request() -> AnalystRunRequest:
    content = "# deterministic role pipeline\n"
    return AnalystRunRequest(
        task=task_request(),
        context=ContextBundle(
            workspace_fingerprint=sha256(content.encode()).hexdigest(),
            documents=(
                ContextDocument(
                    path="TASK.md",
                    content=content,
                    size_bytes=len(content.encode()),
                    sha256=sha256(content.encode()).hexdigest(),
                ),
            ),
            total_bytes=len(content.encode()),
        ),
        workflow_id="workflow-role-pipeline",
        correlation_id="correlation-role-pipeline",
        configuration_fingerprint="b" * 64,
        budget_limits=budget_limits(),
    )


def _advance(
    snapshot: RolePipelineSnapshot,
    transitions: tuple[TransitionCommand, ...],
    **updates: object,
) -> RolePipelineSnapshot:
    if snapshot.state is None:
        state = initial_state(
            snapshot.request.task,
            workflow_id=snapshot.request.workflow_id,
            correlation_id=snapshot.request.correlation_id,
            limits=snapshot.request.budget_limits,
        )
        events = ()
    else:
        state, events = snapshot.state, snapshot.events
    for command in transitions:
        state, events = append_transition(state, command, events)
    return snapshot.model_copy(update={"state": state, "events": events, **updates})


def _command(
    command_id: str,
    target: Stage,
    second: int,
    *,
    actor: str = "workflow",
    artifact=None,
    reason: str | None = None,
) -> TransitionCommand:
    return TransitionCommand(
        command_id=command_id,
        task_id="TASK-001",
        actor_id=actor,
        target_stage=target,
        occurred_at=at(second),
        artifact=artifact,
        charge=BudgetCharge(rework_attempts=1 if target is Stage.REWORK else 0),
        reason=reason,
    )


def _handlers(calls: list[str]) -> RolePipelineHandlers:
    async def analyst(snapshot: RolePipelineSnapshot) -> RolePipelineSnapshot:
        calls.append("analyst")
        requirements = requirements_analysis_report()
        handoff = PMRequirementsHandoff(
            workflow_id=snapshot.request.workflow_id,
            task=snapshot.request.task,
            analysis=requirements,
            unresolved_questions=(),
            configuration_fingerprint=snapshot.request.configuration_fingerprint,
        )
        return _advance(
            snapshot,
            (
                _command("role-command-01", Stage.ANALYZING, 1),
                _command(
                    "role-command-02",
                    Stage.ANALYSIS_READY,
                    2,
                    actor="analyst",
                    artifact=requirements,
                ),
            ),
            requirements=requirements,
            handoff=handoff,
        )

    async def pm(snapshot: RolePipelineSnapshot) -> RolePipelineSnapshot:
        calls.append("pm")
        artifact = specification()
        return _advance(
            snapshot,
            (
                _command("role-command-03", Stage.SPECIFYING, 3),
                _command("role-command-04", Stage.SPEC_READY, 4, actor="pm", artifact=artifact),
            ),
            specification=artifact,
        )

    async def data_engineer(snapshot: RolePipelineSnapshot) -> RolePipelineSnapshot:
        calls.append("data_engineer")
        artifact = implementation_result()
        return _advance(
            snapshot,
            (
                _command("role-command-05", Stage.IMPLEMENTING, 5),
                _command(
                    "role-command-06",
                    Stage.IMPLEMENTED,
                    6,
                    actor="data-engineer",
                    artifact=artifact,
                ),
            ),
            analysis=analysis_report(),
            implementation=artifact,
        )

    async def validator(snapshot: RolePipelineSnapshot) -> RolePipelineSnapshot:
        calls.append("validator")
        artifact = validation_result()
        return _advance(
            snapshot,
            (
                _command("role-command-07", Stage.VALIDATING, 7),
                _command(
                    "role-command-08",
                    Stage.VALIDATED,
                    8,
                    actor="validator",
                    artifact=artifact,
                ),
            ),
            validation=artifact,
        )

    async def qa(snapshot: RolePipelineSnapshot) -> RolePipelineSnapshot:
        calls.append("qa")
        artifact = qa_report()
        return _advance(
            snapshot,
            (
                _command("role-command-09", Stage.QA, 9),
                _command("role-command-10", Stage.QA_PASSED, 10, actor="qa", artifact=artifact),
            ),
            qa_report=artifact,
        )

    async def reviewer(snapshot: RolePipelineSnapshot) -> RolePipelineSnapshot:
        calls.append("reviewer")
        artifact = review_report()
        return _advance(
            snapshot,
            (
                _command("role-command-11", Stage.REVIEW, 11),
                _command("role-command-12", Stage.DONE, 12, actor="reviewer", artifact=artifact),
            ),
            review_report=artifact,
        )

    return RolePipelineHandlers(analyst, pm, data_engineer, validator, qa, reviewer)


def test_six_role_graph_reaches_done_and_checkpoints_every_boundary(tmp_path: Path) -> None:
    calls: list[str] = []
    storage = SecureCheckpointStorage(tmp_path, tmp_path / "checkpoints")
    receipts = SecureRoleReceiptStore(tmp_path, tmp_path / "receipts")
    workflow = build_role_pipeline(_handlers(calls), storage, receipts)

    result = asyncio.run(workflow.run(initial_role_message(_request())))
    snapshot = decode_role_snapshot(result.get_outputs()[0])
    checkpoints = asyncio.run(storage.list_checkpoints(workflow_name=workflow.name))

    assert calls == ["analyst", "pm", "data_engineer", "validator", "qa", "reviewer"]
    assert snapshot.state is not None and snapshot.state.stage is Stage.DONE
    assert snapshot.state.revision == 12
    assert workflow.max_iterations == 32
    assert sorted(item.iteration_count for item in checkpoints) == list(range(8))
    assert all(
        "runtime.role_pipeline" not in path.read_text(encoding="utf-8")
        for path in storage.storage_path.glob("*.json")
    )


def test_role_boundary_rejects_wrong_stage_before_handler_call() -> None:
    called = False

    async def stage(snapshot: RolePipelineSnapshot) -> RolePipelineSnapshot:
        nonlocal called
        called = True
        return snapshot

    executor = PMExecutor(
        "role_pm",
        stage,
        frozenset({Stage.ANALYSIS_READY}),
        frozenset({Stage.SPEC_READY}),
    )
    with pytest.raises(RoleBoundaryError, match="analysis_ready"):
        asyncio.run(executor.advance(initial_role_message(_request())))
    assert called is False


def test_role_boundary_rejects_tampered_event_chain() -> None:
    calls: list[str] = []
    initial = RolePipelineSnapshot(request=_request())
    accepted = asyncio.run(_handlers(calls).analyst(initial))
    assert accepted.state is not None
    tampered = accepted.model_copy(
        update={"state": accepted.state.model_copy(update={"revision": 99})}
    )

    with pytest.raises(RoleBoundaryError, match="failed validation"):
        decode_role_snapshot(encode_role_snapshot(tampered))


def test_pm_blocked_routes_directly_to_terminal(tmp_path: Path) -> None:
    calls: list[str] = []
    base = _handlers(calls)

    async def blocked_pm(snapshot: RolePipelineSnapshot) -> RolePipelineSnapshot:
        calls.append("pm")
        artifact = specification(decision=SpecificationDecision.BLOCKED)
        return _advance(
            snapshot,
            (
                _command("blocked-command-03", Stage.SPECIFYING, 3),
                _command(
                    "blocked-command-04",
                    Stage.BLOCKED,
                    4,
                    actor="pm",
                    artifact=artifact,
                    reason="needs_user",
                ),
            ),
            specification=artifact,
        )

    storage = SecureCheckpointStorage(tmp_path, tmp_path / "checkpoints")
    receipts = SecureRoleReceiptStore(tmp_path, tmp_path / "receipts")
    workflow = build_role_pipeline(replace(base, pm=blocked_pm), storage, receipts)
    result = asyncio.run(workflow.run(initial_role_message(_request())))
    snapshot = decode_role_snapshot(result.get_outputs()[0])

    assert snapshot.state is not None and snapshot.state.stage is Stage.BLOCKED
    assert calls == ["analyst", "pm"]


def test_validator_rework_returns_to_de_then_repeats_all_quality_gates(tmp_path: Path) -> None:
    calls: list[str] = []
    base = _handlers(calls)
    validator_attempt = 0

    async def repairing_de(snapshot: RolePipelineSnapshot) -> RolePipelineSnapshot:
        if snapshot.state is not None and snapshot.state.stage is Stage.SPEC_READY:
            return await base.data_engineer(snapshot)
        calls.append("data_engineer")
        artifact = implementation_result(artifact_id="artifact-implementation-2")
        rolled = tuple(
            item
            for item in (
                snapshot.implementation,
                snapshot.validation,
                snapshot.qa_report,
                snapshot.review_report,
            )
            if item is not None
        )
        return _advance(
            snapshot,
            (
                _command("rework-command-09", Stage.IMPLEMENTING, 9),
                _command(
                    "rework-command-10",
                    Stage.IMPLEMENTED,
                    10,
                    actor="data-engineer",
                    artifact=artifact,
                ),
            ),
            gate_history=(*snapshot.gate_history, *rolled),
            implementation=artifact,
            validation=None,
            qa_report=None,
            review_report=None,
        )

    async def flaky_validator(snapshot: RolePipelineSnapshot) -> RolePipelineSnapshot:
        nonlocal validator_attempt
        calls.append("validator")
        validator_attempt += 1
        failed = validator_attempt == 1
        artifact = validation_result(
            decision=ValidationDecision.FAIL if failed else ValidationDecision.PASS,
            artifact_id=f"artifact-validation-{validator_attempt}",
        )
        start = 7 if failed else 11
        target = Stage.REWORK if failed else Stage.VALIDATED
        return _advance(
            snapshot,
            (
                _command(f"validator-start-{validator_attempt}", Stage.VALIDATING, start),
                _command(
                    f"validator-result-{validator_attempt}",
                    target,
                    start + 1,
                    actor="validator",
                    artifact=artifact,
                    reason="validation failed" if failed else None,
                ),
            ),
            validation=artifact,
        )

    async def late_qa(snapshot: RolePipelineSnapshot) -> RolePipelineSnapshot:
        calls.append("qa")
        artifact = qa_report()
        return _advance(
            snapshot,
            (
                _command("late-qa-start", Stage.QA, 13),
                _command("late-qa-result", Stage.QA_PASSED, 14, actor="qa", artifact=artifact),
            ),
            qa_report=artifact,
        )

    async def late_reviewer(snapshot: RolePipelineSnapshot) -> RolePipelineSnapshot:
        calls.append("reviewer")
        artifact = review_report()
        return _advance(
            snapshot,
            (
                _command("late-review-start", Stage.REVIEW, 15),
                _command("late-review-result", Stage.DONE, 16, actor="reviewer", artifact=artifact),
            ),
            review_report=artifact,
        )

    handlers = replace(
        base,
        data_engineer=repairing_de,
        validator=flaky_validator,
        qa=late_qa,
        reviewer=late_reviewer,
    )
    storage = SecureCheckpointStorage(tmp_path, tmp_path / "checkpoints")
    receipts = SecureRoleReceiptStore(tmp_path, tmp_path / "receipts")
    workflow = build_role_pipeline(handlers, storage, receipts)
    result = asyncio.run(workflow.run(initial_role_message(_request())))
    snapshot = decode_role_snapshot(result.get_outputs()[0])

    assert snapshot.state is not None and snapshot.state.stage is Stage.DONE
    assert snapshot.state.budgets.used.rework_attempts == 1
    assert calls == [
        "analyst",
        "pm",
        "data_engineer",
        "validator",
        "data_engineer",
        "validator",
        "qa",
        "reviewer",
    ]
    assert [item.artifact_id for item in snapshot.gate_history] == [
        "artifact-implementation-1",
        "artifact-validation-1",
    ]


def test_rework_budget_exhaustion_routes_failed_to_terminal(tmp_path: Path) -> None:
    calls: list[str] = []
    base = _handlers(calls)

    async def failed_validator(snapshot: RolePipelineSnapshot) -> RolePipelineSnapshot:
        calls.append("validator")
        artifact = validation_result(
            decision=ValidationDecision.FAIL, artifact_id="artifact-validation-no-budget"
        )
        return _advance(
            snapshot,
            (
                _command("exhaust-start", Stage.VALIDATING, 7),
                _command(
                    "exhaust-result",
                    Stage.REWORK,
                    8,
                    actor="validator",
                    artifact=artifact,
                    reason="validation failed",
                ),
            ),
            validation=artifact,
        )

    request = _request().model_copy(update={"budget_limits": budget_limits(rework_attempts=0)})
    storage = SecureCheckpointStorage(tmp_path, tmp_path / "checkpoints")
    receipts = SecureRoleReceiptStore(tmp_path, tmp_path / "receipts")
    workflow = build_role_pipeline(replace(base, validator=failed_validator), storage, receipts)
    result = asyncio.run(workflow.run(initial_role_message(request)))
    snapshot = decode_role_snapshot(result.get_outputs()[0])

    assert snapshot.state is not None and snapshot.state.stage is Stage.FAILED
    assert calls == ["analyst", "pm", "data_engineer", "validator"]


@pytest.mark.parametrize("failing_gate", ["qa", "reviewer"])
def test_qa_and_reviewer_rework_route_back_to_de(tmp_path: Path, failing_gate: str) -> None:
    calls: list[str] = []
    base = _handlers(calls)

    async def gate_qa(snapshot: RolePipelineSnapshot) -> RolePipelineSnapshot:
        if failing_gate == "reviewer":
            return await base.qa(snapshot)
        calls.append("qa")
        artifact = qa_report(decision=QADecision.FAIL)
        return _advance(
            snapshot,
            (
                _command("failing-qa-start", Stage.QA, 9),
                _command(
                    "failing-qa-result",
                    Stage.REWORK,
                    10,
                    actor="qa",
                    artifact=artifact,
                    reason="QA failed",
                ),
            ),
            qa_report=artifact,
        )

    async def gate_reviewer(snapshot: RolePipelineSnapshot) -> RolePipelineSnapshot:
        calls.append("reviewer")
        artifact = review_report(decision=ReviewDecision.REQUEST_CHANGES)
        return _advance(
            snapshot,
            (
                _command("failing-review-start", Stage.REVIEW, 11),
                _command(
                    "failing-review-result",
                    Stage.REWORK,
                    12,
                    actor="reviewer",
                    artifact=artifact,
                    reason="review failed",
                ),
            ),
            review_report=artifact,
        )

    async def blocked_repair(snapshot: RolePipelineSnapshot) -> RolePipelineSnapshot:
        if snapshot.state is not None and snapshot.state.stage is Stage.SPEC_READY:
            return await base.data_engineer(snapshot)
        calls.append("data_engineer")
        artifact = implementation_result(
            artifact_id=f"artifact-blocked-after-{failing_gate}",
            status=ImplementationStatus.BLOCKED,
        )
        rolled = tuple(
            item
            for item in (
                snapshot.implementation,
                snapshot.validation,
                snapshot.qa_report,
                snapshot.review_report,
            )
            if item is not None
        )
        start = 11 if failing_gate == "qa" else 13
        return _advance(
            snapshot,
            (
                _command(f"blocked-repair-{failing_gate}-start", Stage.IMPLEMENTING, start),
                _command(
                    f"blocked-repair-{failing_gate}-result",
                    Stage.BLOCKED,
                    start + 1,
                    actor="data-engineer",
                    artifact=artifact,
                    reason="repair blocked",
                ),
            ),
            gate_history=(*snapshot.gate_history, *rolled),
            implementation=artifact,
            validation=None,
            qa_report=None,
            review_report=None,
        )

    handlers = replace(
        base,
        data_engineer=blocked_repair,
        qa=gate_qa,
        reviewer=gate_reviewer,
    )
    storage = SecureCheckpointStorage(tmp_path, tmp_path / "checkpoints")
    receipts = SecureRoleReceiptStore(tmp_path, tmp_path / "receipts")
    workflow = build_role_pipeline(handlers, storage, receipts)
    result = asyncio.run(workflow.run(initial_role_message(_request())))
    snapshot = decode_role_snapshot(result.get_outputs()[0])

    assert snapshot.state is not None and snapshot.state.stage is Stage.BLOCKED
    assert calls[-1] == "data_engineer"
    assert calls.count("data_engineer") == 2
