import asyncio
from collections.abc import Iterator
from datetime import datetime

import pytest

from contracts import PMRequirementsHandoff, RequirementsAnalysisReport, SpecificationDecision
from orchestrator import (
    BudgetExceededError,
    EventChainError,
    Stage,
    TransitionCommand,
    append_transition,
    initial_state,
    verify_event_chain,
)
from runtime.agent_runtime import (
    PMBoundaryError,
    SpecificationRunRequest,
    build_specification_workflow,
)
from runtime.model_provider import MAFModelProvider, ModelOutputValidationError
from tests.fakes import StaticChatClient, gate_settings
from tests.workflow.factories import at, budget_limits, requirements_analysis_report, task_request

QUESTION = "Should late refunds restate prior dates?"


def fixed_clock(*seconds: int):
    values: Iterator[datetime] = iter(at(second) for second in seconds)
    return lambda: next(values)


def pm_request(
    *,
    unresolved_questions: tuple[str, ...] = (),
    model_token_limit: int = 100,
) -> SpecificationRunRequest:
    task = task_request()
    report_payload = requirements_analysis_report().model_dump()
    report_payload["open_questions"] = unresolved_questions
    report = RequirementsAnalysisReport.model_validate(report_payload)
    limits = budget_limits().model_copy(update={"model_tokens": model_token_limit})
    state = initial_state(
        task,
        workflow_id="workflow-agent-1",
        correlation_id="correlation-agent-1",
        limits=limits,
    )
    state, events = append_transition(
        state,
        TransitionCommand(
            command_id="command-analyzing",
            task_id=task.task_id,
            actor_id="workflow",
            target_stage=Stage.ANALYZING,
            occurred_at=at(1),
        ),
        (),
    )
    state, events = append_transition(
        state,
        TransitionCommand(
            command_id="command-analysis-ready",
            task_id=task.task_id,
            actor_id=report.producer_id,
            target_stage=Stage.ANALYSIS_READY,
            occurred_at=at(2),
            artifact=report,
        ),
        events,
    )
    return SpecificationRunRequest(
        handoff=PMRequirementsHandoff(
            workflow_id=state.workflow_id,
            task=task,
            analysis=report,
            unresolved_questions=unresolved_questions,
            configuration_fingerprint="b" * 64,
        ),
        state=state,
        events=events,
    )


def run_workflow(
    payload: str,
    *,
    request: SpecificationRunRequest | None = None,
):
    client = StaticChatClient(payload)
    provider = MAFModelProvider(gate_settings(), client=client)
    workflow = build_specification_workflow(provider, clock=fixed_clock(3, 4))
    result = asyncio.run(workflow.run(request or pm_request()))
    outputs = result.get_outputs()
    assert len(outputs) == 1
    return outputs[0], client


def test_pm_accepts_ready_specification_from_resolved_handoff() -> None:
    output, client = run_workflow(
        """{
          "decision": "ready",
          "business_goal": "Expose Net Revenue.",
          "metric_definition": "successful payments minus successful refunds",
          "grain": ["order_date", "country", "channel", "currency"],
          "dimensions": ["country", "channel", "currency"],
          "source_requirements": ["orders", "payments", "refunds"],
          "acceptance_criteria": ["metric identity holds"]
        }"""
    )

    assert output.artifact.decision is SpecificationDecision.READY
    assert output.artifact.blocked_reason is None
    assert output.artifact.task_id == "TASK-001"
    assert output.artifact.producer_id == "pm-agent"
    assert output.state.stage is Stage.SPEC_READY
    assert output.state.budgets.used.model_tokens == 15
    assert len(output.events) == 4
    assert "artifacts/TASK-001" not in str(client.messages)
    assert client.options.get("tools") in (None, [])
    verify_event_chain(output.events, expected_state=output.state)


def test_pm_routes_unresolved_handoff_to_typed_needs_user() -> None:
    output, _ = run_workflow(
        f"""{{
          "decision": "blocked",
          "business_goal": "Expose a trusted metric.",
          "open_questions": ["{QUESTION}"]
        }}""",
        request=pm_request(unresolved_questions=(QUESTION,)),
    )

    assert output.state.stage is Stage.BLOCKED
    assert output.state.terminal_reason == "needs_user"
    assert output.artifact.blocked_reason.value == "needs_user"
    assert output.artifact.open_questions == (QUESTION,)


@pytest.mark.parametrize(
    "payload",
    [
        """{
          "decision": "ready",
          "business_goal": "Assume an answer.",
          "metric_definition": "invented",
          "grain": ["day"],
          "dimensions": ["country"],
          "source_requirements": ["orders"],
          "acceptance_criteria": ["returns rows"]
        }""",
        """{
          "decision": "blocked",
          "business_goal": "Expose a trusted metric.",
          "open_questions": ["A different question?"]
        }""",
    ],
)
def test_pm_cannot_erase_or_replace_analyst_questions(payload: str) -> None:
    with pytest.raises(PMBoundaryError, match=r"unresolved|preserve"):
        run_workflow(payload, request=pm_request(unresolved_questions=(QUESTION,)))


def test_pm_rejects_forged_chain_handoff_and_identity_before_model_call() -> None:
    request = pm_request()
    for invalid in (
        request.model_copy(update={"events": request.events[:-1]}),
        request.model_copy(
            update={"handoff": request.handoff.model_copy(update={"workflow_id": "foreign"})}
        ),
        request.model_copy(
            update={
                "handoff": request.handoff.model_copy(
                    update={"task": request.handoff.task.model_copy(update={"task_id": "OTHER"})}
                )
            }
        ),
        request.model_copy(
            update={
                "handoff": request.handoff.model_copy(
                    update={
                        "analysis": request.handoff.analysis.model_copy(
                            update={"artifact_id": "forged-analysis"}
                        )
                    }
                )
            }
        ),
        request.model_copy(update={"agent_id": request.handoff.analysis.producer_id}),
    ):
        with pytest.raises((EventChainError, PMBoundaryError)):
            run_workflow("{}", request=invalid)


def test_pm_fails_closed_on_malformed_output_and_measured_budget() -> None:
    with pytest.raises(ModelOutputValidationError):
        run_workflow("not-json")
    with pytest.raises(BudgetExceededError, match="model_tokens"):
        run_workflow(
            """{
              "decision": "blocked",
              "business_goal": "Expose a trusted metric.",
              "open_questions": ["What is the definition?"]
            }""",
            request=pm_request(model_token_limit=14),
        )
