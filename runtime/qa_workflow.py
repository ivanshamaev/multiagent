"""MAF workflow for one independent, read-only QA assessment."""

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
    tool,
)

from contracts import (
    ClickHouseRunQueryCall,
    QAReport,
    ToolCallEvidence,
    tool_arguments_sha256,
)
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
from runtime.qa import (
    QA_SEMANTIC_PROBE_SQL,
    QADraft,
    QAInspectionDraft,
    QARunRequest,
    accept_qa_draft,
    qa_system_prompt,
    qa_user_prompt,
)
from runtime.tools import ConnectedDataEngineerMCPTools


class QAWorkflowInput(FrozenModel):
    request: QARunRequest
    state: WorkflowState
    events: tuple[WorkflowEvent, ...]


class AutonomousQAResult(FrozenModel):
    report: QAReport
    state: WorkflowState
    events: tuple[WorkflowEvent, ...]
    tool_evidence: tuple[ToolCallEvidence, ...]
    model_calls: tuple[ModelCallRecord, ...]


class AutonomousQAError(RuntimeError):
    """Safe metadata for a QA attempt that cannot cross the domain boundary."""

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


def _tools_named(
    connected: ConnectedDataEngineerMCPTools,
    names: frozenset[str],
) -> tuple[FunctionTool, ...]:
    selected = tuple(item for item in connected.tools if item.name in names)
    if {item.name for item in selected} != names:
        raise ValueError("QA profile does not expose the exact phase tool set")
    return selected


def _public_probe_tool(
    connected: ConnectedDataEngineerMCPTools,
) -> tuple[FunctionTool, ...]:
    underlying = _tools_named(connected, frozenset({"clickhouse_run_query"}))[0]

    @tool(
        name="qa_run_public_probe",
        description="Run the immutable code-owned Net Revenue semantic comparison probe.",
        approval_mode="never_require",
    )
    async def qa_run_public_probe() -> str:
        result = await underlying.invoke(arguments={"query": QA_SEMANTIC_PROBE_SQL})
        return str(result)

    return (qa_run_public_probe,)


def _aggregate_usage(records: tuple[ModelCallRecord, ...]) -> ModelUsage:
    return ModelUsage(
        input_tokens=sum(item.usage.input_tokens for item in records),
        output_tokens=sum(item.usage.output_tokens for item in records),
        total_tokens=sum(item.usage.total_tokens for item in records),
    )


class AutonomousQAExecutor(Executor):
    """Run two fresh least-privilege QA phases and assemble a code-owned report."""

    def __init__(
        self,
        provider: ToolEnabledStructuredModelProvider,
        connected_tools: ConnectedDataEngineerMCPTools,
        *,
        clock: Callable[[], UtcDateTime] | None = None,
    ) -> None:
        super().__init__(id="autonomous_qa")
        self.provider = provider
        self.connected_tools = connected_tools
        self.now = clock or (lambda: datetime.now(UTC))

    @handler
    async def run_assessment(
        self,
        workflow_input: QAWorkflowInput,
        ctx: WorkflowContext[Never, AutonomousQAResult],
    ) -> None:
        request = workflow_input.request
        state = workflow_input.state
        events = workflow_input.events
        verify_event_chain(events, expected_state=state)
        base_prompt = qa_user_prompt(request)
        read_tools = _tools_named(self.connected_tools, frozenset({"workspace_read_file"}))
        query_tools = _public_probe_tool(self.connected_tools)
        try:
            inspection = await self.provider.generate_with_tools(
                QAInspectionDraft,
                system_prompt=(
                    f"{qa_system_prompt()}\n\n"
                    "INSPECTION PHASE: call workspace_read_file exactly once with path "
                    "platform/dbt/models/marts/fct_net_revenue.sql. Do not write or query. "
                    "Then return findings and a probe strategy."
                ),
                user_prompt=base_prompt,
                tools=read_tools,
            )
        except ModelInvocationError as error:
            failed_records = (
                (error.model_call,) if isinstance(error, ModelOutputValidationError) else ()
            )
            raise AutonomousQAError(
                "qa_inspection_model_failure",
                model_calls=failed_records,
                tool_evidence=self.connected_tools.gateway.evidence,
                error_fingerprint=str(error),
            ) from None
        records = (model_call_record(inspection),)
        if len(self.connected_tools.gateway.evidence) != 1:
            raise AutonomousQAError(
                "qa_inspection_requires_exactly_one_read",
                model_calls=records,
                tool_evidence=self.connected_tools.gateway.evidence,
            )
        inspection_context = inspection.value.model_dump_json()
        try:
            decision = await self.provider.generate_with_tools(
                QADraft,
                system_prompt=(
                    f"{qa_system_prompt()}\n\n"
                    "PROBE PHASE: call qa_run_public_probe exactly once. The tool executes an "
                    "immutable code-owned public semantic comparison. An empty result supports "
                    "PASS and must not become a hypothetical SQL defect; any returned mismatch "
                    "row supports FAIL. Only a concrete missing or tautological required candidate "
                    "test may fail an empty semantic diff. Interpret the result, then return the "
                    "structured QA decision."
                ),
                user_prompt=(
                    f"{base_prompt}\n<untrusted_prior_inspection>{inspection_context}"
                    "</untrusted_prior_inspection>"
                ),
                tools=query_tools,
            )
        except ModelInvocationError as error:
            failed_records = (
                (*records, error.model_call)
                if isinstance(error, ModelOutputValidationError)
                else records
            )
            raise AutonomousQAError(
                "qa_probe_model_failure",
                model_calls=failed_records,
                tool_evidence=self.connected_tools.gateway.evidence,
                error_fingerprint=str(error),
            ) from None
        records = (*records, model_call_record(decision))
        tool_evidence = self.connected_tools.gateway.evidence
        if len(tool_evidence) != 2:
            raise AutonomousQAError(
                "qa_probe_requires_exactly_one_query",
                model_calls=records,
                tool_evidence=tool_evidence,
            )
        expected_arguments = tool_arguments_sha256(
            ClickHouseRunQueryCall(query=QA_SEMANTIC_PROBE_SQL)
        )
        if tool_evidence[-1].arguments_sha256 != expected_arguments:
            raise AutonomousQAError(
                "qa_probe_query_did_not_match_public_plan",
                model_calls=records,
                tool_evidence=tool_evidence,
            )
        completed_at = max([self.now(), *(item.completed_at for item in tool_evidence)])
        report, state, events = accept_qa_draft(
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
            AutonomousQAResult(
                report=report,
                state=state,
                events=events,
                tool_evidence=tool_evidence,
                model_calls=records,
            )
        )


def build_qa_workflow(
    provider: ToolEnabledStructuredModelProvider,
    connected_tools: ConnectedDataEngineerMCPTools,
    *,
    clock: Callable[[], UtcDateTime] | None = None,
) -> Workflow:
    """Build the caller-scoped QA graph."""

    executor = AutonomousQAExecutor(provider, connected_tools, clock=clock)
    return WorkflowBuilder(start_executor=executor, output_from=[executor]).build()
