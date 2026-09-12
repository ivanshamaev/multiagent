"""MAF workflow for one independent read-only Reviewer assessment."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Never

from agent_framework import (
    Executor,
    FunctionTool,
    Workflow,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)

from contracts import ReviewReport, ToolCallEvidence, WorkspaceReadCall, tool_arguments_sha256
from contracts.common import FrozenModel, UtcDateTime
from orchestrator import WorkflowEvent, WorkflowState, verify_event_chain
from runtime.model_provider import (
    ModelCallRecord,
    ModelInvocationError,
    ModelOutputValidationError,
    ModelUsage,
    ToolEnabledStructuredModelProvider,
    model_call_record,
)
from runtime.reviewer import (
    ReviewerDraft,
    ReviewerInspectionDraft,
    ReviewerRunRequest,
    accept_reviewer_draft,
    reviewer_system_prompt,
    reviewer_user_prompt,
)
from runtime.tools import ConnectedDataEngineerMCPTools

MODEL_PATH = "platform/dbt/models/marts/fct_net_revenue.sql"
TEST_PATH = "platform/dbt/tests/assert_fct_net_revenue_contract.sql"


class ReviewerWorkflowInput(FrozenModel):
    request: ReviewerRunRequest
    state: WorkflowState
    events: tuple[WorkflowEvent, ...]


class AutonomousReviewerResult(FrozenModel):
    report: ReviewReport
    state: WorkflowState
    events: tuple[WorkflowEvent, ...]
    tool_evidence: tuple[ToolCallEvidence, ...]
    model_calls: tuple[ModelCallRecord, ...]


class AutonomousReviewerError(RuntimeError):
    """Safe metadata for a Reviewer attempt rejected at its trust boundary."""

    def __init__(
        self,
        code: str,
        *,
        model_calls: tuple[ModelCallRecord, ...],
        tool_evidence: tuple[ToolCallEvidence, ...],
        error_fingerprint: str | None = None,
    ) -> None:
        super().__init__(code)
        self.code = code
        self.model_calls = model_calls
        self.tool_evidence = tool_evidence
        self.error_fingerprint = error_fingerprint


def _read_tool(connected: ConnectedDataEngineerMCPTools) -> tuple[FunctionTool, ...]:
    selected = tuple(item for item in connected.tools if item.name == "workspace_read_file")
    if len(selected) != 1:
        raise ValueError("Reviewer profile must expose exactly one workspace read tool")
    return selected


def _aggregate_usage(records: tuple[ModelCallRecord, ...]) -> ModelUsage:
    return ModelUsage(
        input_tokens=sum(item.usage.input_tokens for item in records),
        output_tokens=sum(item.usage.output_tokens for item in records),
        total_tokens=sum(item.usage.total_tokens for item in records),
    )


class AutonomousReviewerExecutor(Executor):
    """Run two fresh exact-read phases and assemble a code-owned review report."""

    def __init__(
        self,
        provider: ToolEnabledStructuredModelProvider,
        connected_tools: ConnectedDataEngineerMCPTools,
        *,
        clock: Callable[[], UtcDateTime] | None = None,
    ) -> None:
        super().__init__(id="autonomous_reviewer")
        self.provider = provider
        self.connected_tools = connected_tools
        self.now = clock or (lambda: datetime.now(UTC))

    @handler
    async def run_review(
        self,
        workflow_input: ReviewerWorkflowInput,
        ctx: WorkflowContext[Never, AutonomousReviewerResult],
    ) -> None:
        request = workflow_input.request
        state = workflow_input.state
        events = workflow_input.events
        verify_event_chain(events, expected_state=state)
        base_prompt = reviewer_user_prompt(request)
        read_tool = _read_tool(self.connected_tools)
        try:
            inspection = await self.provider.generate_with_tools(
                ReviewerInspectionDraft,
                system_prompt=(
                    f"{reviewer_system_prompt()}\n\n"
                    f"MODEL PHASE: call workspace_read_file exactly once with path {MODEL_PATH}. "
                    "Inspect maintainability, deterministic attribution, dbt portability and "
                    "security boundaries. Preserve concrete positive observations as well as "
                    "findings and risks so the fresh decision phase can assess the model; include "
                    "its materialization, projections, grain, numeric types, source/ref usage, "
                    "event semantics, currency handling, and tie-breaks. Do not decide yet."
                ),
                user_prompt=base_prompt,
                tools=read_tool,
            )
        except ModelInvocationError as error:
            failed = (error.model_call,) if isinstance(error, ModelOutputValidationError) else ()
            raise AutonomousReviewerError(
                "reviewer_model_inspection_failure",
                model_calls=failed,
                tool_evidence=self.connected_tools.gateway.evidence,
                error_fingerprint=str(error),
            ) from None
        records = (model_call_record(inspection),)
        if len(self.connected_tools.gateway.evidence) != 1:
            raise AutonomousReviewerError(
                "reviewer_requires_exactly_one_model_read",
                model_calls=records,
                tool_evidence=self.connected_tools.gateway.evidence,
            )
        try:
            decision = await self.provider.generate_with_tools(
                ReviewerDraft,
                system_prompt=(
                    f"{reviewer_system_prompt()}\n\n"
                    f"TEST AND DECISION PHASE: call workspace_read_file exactly once with path "
                    f"{TEST_PATH}. Assess every immutable acceptance criterion exactly once using "
                    "its verbatim criterion text. The accepted QA PASS is authoritative evidence "
                    "that the full validator and immutable semantic probe passed; do not demand "
                    "that this one singular test duplicate those gates. Request changes only for "
                    "a concrete candidate defect. In this specification, the candidate-test scope "
                    "is exactly required fields, grain uniqueness, and metric identity; absence "
                    "of additional event-semantic assertions is not a defect. Treat the prior "
                    "inspection as the evidence-preserving result of the first model-file read. "
                    "If it contains no concrete defect and this test implements its stated scope, "
                    "assess all criteria PASS and APPROVE. Otherwise cite the exact visible defect "
                    "and REQUEST_CHANGES. Then return the structured decision."
                ),
                user_prompt=(
                    f"{base_prompt}\n<untrusted_model_inspection>"
                    f"{inspection.value.model_dump_json()}</untrusted_model_inspection>"
                ),
                tools=read_tool,
            )
        except ModelInvocationError as error:
            failed = (
                (*records, error.model_call)
                if isinstance(error, ModelOutputValidationError)
                else records
            )
            raise AutonomousReviewerError(
                "reviewer_test_decision_failure",
                model_calls=failed,
                tool_evidence=self.connected_tools.gateway.evidence,
                error_fingerprint=str(error),
            ) from None
        records = (*records, model_call_record(decision))
        tool_evidence = self.connected_tools.gateway.evidence
        if len(tool_evidence) != 2:
            raise AutonomousReviewerError(
                "reviewer_requires_exactly_two_reads",
                model_calls=records,
                tool_evidence=tool_evidence,
            )
        expected_hashes = (
            tool_arguments_sha256(WorkspaceReadCall(path=MODEL_PATH)),
            tool_arguments_sha256(WorkspaceReadCall(path=TEST_PATH)),
        )
        if tuple(item.arguments_sha256 for item in tool_evidence) != expected_hashes:
            raise AutonomousReviewerError(
                "reviewer_read_paths_did_not_match_plan",
                model_calls=records,
                tool_evidence=tool_evidence,
            )
        completed_at = max(self.now(), *(item.completed_at for item in tool_evidence))
        report, state, events = accept_reviewer_draft(
            request,
            state,
            events,
            decision.value,
            tool_evidence=tool_evidence,
            tool_usage=self.connected_tools.gateway.usage,
            model_usage=_aggregate_usage(records),
            model_latency_ms=sum(item.latency_ms for item in records),
            completed_at=completed_at,
        )
        await ctx.yield_output(
            AutonomousReviewerResult(
                report=report,
                state=state,
                events=events,
                tool_evidence=tool_evidence,
                model_calls=records,
            )
        )


def build_reviewer_workflow(
    provider: ToolEnabledStructuredModelProvider,
    connected_tools: ConnectedDataEngineerMCPTools,
    *,
    clock: Callable[[], UtcDateTime] | None = None,
) -> Workflow:
    executor = AutonomousReviewerExecutor(provider, connected_tools, clock=clock)
    return WorkflowBuilder(start_executor=executor, output_from=[executor]).build()
