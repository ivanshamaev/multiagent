import asyncio
from collections.abc import Iterator
from datetime import datetime

import pytest

from contracts import SpecificationDecision
from orchestrator import BudgetExceededError, Stage, verify_event_chain
from runtime.agent_runtime import SpecificationRunRequest, build_specification_workflow
from runtime.model_provider import MAFModelProvider
from tests.fakes import StaticChatClient, context_bundle, gate_settings
from tests.workflow.factories import at, budget_limits, task_request


def fixed_clock(*seconds: int):
    values: Iterator[datetime] = iter(at(second) for second in seconds)
    return lambda: next(values)


def run_workflow(payload: str, *, model_token_limit: int = 100):
    provider = MAFModelProvider(gate_settings(), client=StaticChatClient(payload))
    workflow = build_specification_workflow(provider, clock=fixed_clock(1, 2))
    request = SpecificationRunRequest(
        task=task_request(),
        context=context_bundle(),
        workflow_id="workflow-agent-1",
        correlation_id="correlation-agent-1",
        budget_limits=budget_limits().model_copy(update={"model_tokens": model_token_limit}),
    )
    result = asyncio.run(workflow.run(request))
    outputs = result.get_outputs()
    assert len(outputs) == 1
    return outputs[0]


def test_maf_code_workflow_accepts_ready_specification_through_reducer() -> None:
    output = run_workflow(
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
    assert output.artifact.task_id == "TASK-001"
    assert output.artifact.producer_id == "pm-agent"
    assert output.state.stage is Stage.SPEC_READY
    assert output.state.budgets.used.model_tokens == 15
    assert len(output.events) == 2
    assert len(output.model_call.request_sha256) == 64
    verify_event_chain(output.events, expected_state=output.state)


def test_maf_code_workflow_routes_blocked_specification() -> None:
    output = run_workflow(
        """{
          "decision": "blocked",
          "business_goal": "Expose a trusted metric.",
          "open_questions": ["What is the metric definition?"]
        }"""
    )

    assert output.state.stage is Stage.BLOCKED
    assert output.state.terminal_reason == "specification requires user input"


def test_maf_code_workflow_fails_closed_on_budget_after_measured_usage() -> None:
    with pytest.raises(BudgetExceededError, match="model_tokens"):
        run_workflow(
            """{
              "decision": "blocked",
              "business_goal": "Expose a trusted metric.",
              "open_questions": ["What is the metric definition?"]
            }""",
            model_token_limit=14,
        )
