import asyncio
from hashlib import sha256
from pathlib import Path

import pytest

from contracts import PMRequirementsHandoff
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
) -> TransitionCommand:
    return TransitionCommand(
        command_id=command_id,
        task_id="TASK-001",
        actor_id=actor,
        target_stage=target,
        occurred_at=at(second),
        artifact=artifact,
        charge=BudgetCharge(),
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
    workflow = build_role_pipeline(_handlers(calls), storage)

    result = asyncio.run(workflow.run(initial_role_message(_request())))
    snapshot = decode_role_snapshot(result.get_outputs()[0])
    checkpoints = asyncio.run(storage.list_checkpoints(workflow_name=workflow.name))

    assert calls == ["analyst", "pm", "data_engineer", "validator", "qa", "reviewer"]
    assert snapshot.state is not None and snapshot.state.stage is Stage.DONE
    assert snapshot.state.revision == 12
    assert sorted(item.iteration_count for item in checkpoints) == list(range(7))
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

    executor = PMExecutor("role_pm", stage, Stage.ANALYSIS_READY, Stage.SPEC_READY)
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
