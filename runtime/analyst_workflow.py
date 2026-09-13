"""Fresh-context MAF workflow for read-only requirements discovery."""

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
    DbtGetLineageCall,
    DbtListCall,
    DbtResourceType,
    PMRequirementsHandoff,
    RequirementsAnalysisReport,
    ToolCallEvidence,
    ToolName,
    tool_arguments_sha256,
)
from contracts.common import FrozenModel, UtcDateTime
from orchestrator import WorkflowEvent, WorkflowState
from runtime.analyst import (
    ANALYST_PROFILE_SQL,
    AnalystPhaseDraft,
    AnalystRunRequest,
    AnalystSynthesisDraft,
    accept_analyst_drafts,
    analyst_system_prompt,
    analyst_user_prompt,
    build_pm_requirements_handoff,
    seed_analyst_state,
)
from runtime.model_provider import (
    ModelCallRecord,
    ModelInvocationError,
    ModelOutputValidationError,
    ModelUsage,
    ToolEnabledStructuredModelProvider,
    model_call_record,
)
from runtime.tools import ConnectedDataEngineerMCPTools

ANALYST_LINEAGE_NODE = "model.agentic_data_platform.fct_orders"


class AutonomousAnalystResult(FrozenModel):
    report: RequirementsAnalysisReport
    state: WorkflowState
    events: tuple[WorkflowEvent, ...]
    tool_evidence: tuple[ToolCallEvidence, ...]
    model_calls: tuple[ModelCallRecord, ...]
    handoff: PMRequirementsHandoff


class AutonomousAnalystError(RuntimeError):
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


def _tool_named(connected: ConnectedDataEngineerMCPTools, name: str) -> FunctionTool:
    selected = tuple(item for item in connected.tools if item.name == name)
    if len(selected) != 1:
        raise ValueError("Analyst profile does not expose the exact phase tool")
    return selected[0]


def _tool_text(result: object) -> str:
    if isinstance(result, str):
        return result
    if isinstance(result, (list, tuple)):
        parts = [getattr(item, "text", None) for item in result]
        if parts and all(isinstance(item, str) for item in parts):
            return "\n".join(parts)
    raise RuntimeError("phase tool returned an unsupported content envelope")


def _metadata_tool(
    connected: ConnectedDataEngineerMCPTools, observations: list[str]
) -> tuple[FunctionTool, ...]:
    underlying = _tool_named(connected, "dbt_list")

    @tool(
        name="analyst_list_resources",
        description="List code-selected dbt models and sources.",
        approval_mode="never_require",
    )
    async def analyst_list_resources() -> str:
        result = await underlying.invoke(
            arguments={"resource_type": [DbtResourceType.MODEL, DbtResourceType.SOURCE]}
        )
        rendered = _tool_text(result)
        observations.append(rendered)
        return rendered

    return (analyst_list_resources,)


def _lineage_tool(
    connected: ConnectedDataEngineerMCPTools, observations: list[str]
) -> tuple[FunctionTool, ...]:
    underlying = _tool_named(connected, "dbt_get_lineage_dev")

    @tool(
        name="analyst_get_lineage",
        description="Read code-selected fct_orders lineage.",
        approval_mode="never_require",
    )
    async def analyst_get_lineage() -> str:
        result = await underlying.invoke(arguments={"unique_id": ANALYST_LINEAGE_NODE, "depth": 2})
        rendered = _tool_text(result)
        observations.append(rendered)
        return rendered

    return (analyst_get_lineage,)


def _profile_tool(
    connected: ConnectedDataEngineerMCPTools, observations: list[str]
) -> tuple[FunctionTool, ...]:
    underlying = _tool_named(connected, "clickhouse_run_query")

    @tool(
        name="analyst_profile_orders",
        description="Run a code-owned aggregate orders profile.",
        approval_mode="never_require",
    )
    async def analyst_profile_orders() -> str:
        result = await underlying.invoke(arguments={"query": ANALYST_PROFILE_SQL})
        rendered = _tool_text(result)
        observations.append(rendered)
        return rendered

    return (analyst_profile_orders,)


def _usage(records: tuple[ModelCallRecord, ...]) -> ModelUsage:
    return ModelUsage(
        input_tokens=sum(item.usage.input_tokens for item in records),
        output_tokens=sum(item.usage.output_tokens for item in records),
        total_tokens=sum(item.usage.total_tokens for item in records),
    )


class AutonomousAnalystExecutor(Executor):
    def __init__(
        self,
        provider: ToolEnabledStructuredModelProvider,
        connected_tools: ConnectedDataEngineerMCPTools,
        *,
        clock: Callable[[], UtcDateTime] | None = None,
    ) -> None:
        super().__init__(id="autonomous_analyst")
        self.provider = provider
        self.connected_tools = connected_tools
        self.now = clock or (lambda: datetime.now(UTC))

    @handler
    async def discover(
        self,
        request: AnalystRunRequest,
        ctx: WorkflowContext[Never, AutonomousAnalystResult],
    ) -> None:
        state, events = seed_analyst_state(request, occurred_at=self.now())
        base = analyst_user_prompt(request)
        observations: list[str] = []
        phase_specs = (
            (
                "METADATA PHASE: call analyst_list_resources exactly once; "
                "report only SOURCE or MODEL facts. Every fact.statement must be an exact "
                "verbatim substring copied from the tool result.",
                _metadata_tool(self.connected_tools, observations),
            ),
            (
                "LINEAGE PHASE: call analyst_get_lineage exactly once; report only LINEAGE facts. "
                "Every fact.statement must be an exact verbatim substring copied from the result.",
                _lineage_tool(self.connected_tools, observations),
            ),
            (
                "PROFILE PHASE: call analyst_profile_orders exactly once; "
                "report only aggregate PROFILE facts. Every fact.statement must be an exact "
                "verbatim substring copied from the tool result.",
                _profile_tool(self.connected_tools, observations),
            ),
        )
        drafts: list[AnalystPhaseDraft] = []
        records: tuple[ModelCallRecord, ...] = ()
        evidence: list[ToolCallEvidence] = []
        prior = ""
        for index, (instruction, phase_tools) in enumerate(phase_specs, start=1):
            before = len(self.connected_tools.gateway.evidence)
            try:
                invocation = await self.provider.generate_with_tools(
                    AnalystPhaseDraft,
                    system_prompt=f"{analyst_system_prompt()}\n\n{instruction}",
                    user_prompt=f"{base}\n<untrusted_prior_findings>{prior}</untrusted_prior_findings>",
                    tools=phase_tools,
                )
            except ModelInvocationError as error:
                failed = (
                    (error.model_call,) if isinstance(error, ModelOutputValidationError) else ()
                )
                raise AutonomousAnalystError(
                    f"analyst_phase_{index}_model_failure",
                    model_calls=(*records, *failed),
                    tool_evidence=self.connected_tools.gateway.evidence,
                    error_fingerprint=str(error),
                ) from None
            records = (*records, model_call_record(invocation))
            current = self.connected_tools.gateway.evidence
            if len(current) != before + 1:
                raise AutonomousAnalystError(
                    f"analyst_phase_{index}_requires_exactly_one_tool",
                    model_calls=records,
                    tool_evidence=current,
                )
            evidence.append(current[-1])
            drafts.append(invocation.value)
            prior = "\n".join(item.model_dump_json() for item in drafts)

        try:
            synthesis = await self.provider.generate(
                AnalystSynthesisDraft,
                system_prompt=(
                    f"{analyst_system_prompt()}\n\nSYNTHESIS PHASE: use no tools. "
                    "Separate assumptions, "
                    "open questions, risks and next steps; do not add facts."
                ),
                user_prompt=f"{base}\n<untrusted_observed_facts>{prior}</untrusted_observed_facts>",
            )
        except ModelInvocationError as error:
            failed = (error.model_call,) if isinstance(error, ModelOutputValidationError) else ()
            raise AutonomousAnalystError(
                "analyst_synthesis_model_failure",
                model_calls=(*records, *failed),
                tool_evidence=self.connected_tools.gateway.evidence,
                error_fingerprint=str(error),
            ) from None
        records = (*records, model_call_record(synthesis))
        expected = (
            (
                ToolName.DBT_LIST,
                tool_arguments_sha256(
                    DbtListCall(resource_type=(DbtResourceType.MODEL, DbtResourceType.SOURCE))
                ),
            ),
            (
                ToolName.DBT_GET_LINEAGE_DEV,
                tool_arguments_sha256(DbtGetLineageCall(unique_id=ANALYST_LINEAGE_NODE, depth=2)),
            ),
            (
                ToolName.CLICKHOUSE_RUN_QUERY,
                tool_arguments_sha256(ClickHouseRunQueryCall(query=ANALYST_PROFILE_SQL)),
            ),
        )
        if tuple((item.tool, item.arguments_sha256) for item in evidence) != expected:
            raise AutonomousAnalystError(
                "analyst_probe_plan_mismatch",
                model_calls=records,
                tool_evidence=tuple(evidence),
            )
        completed = max([self.now(), *(item.completed_at for item in evidence)])
        report, state, events = accept_analyst_drafts(
            request,
            state,
            events,
            tuple(drafts),
            synthesis.value,
            phase_evidence=tuple(evidence),
            phase_outputs=tuple(observations),
            tool_usage=self.connected_tools.gateway.usage,
            model_usage=_usage(records),
            model_latency_ms=sum(item.latency_ms for item in records),
            completed_at=completed,
        )
        handoff = build_pm_requirements_handoff(request, report, state)
        await ctx.yield_output(
            AutonomousAnalystResult(
                report=report,
                state=state,
                events=events,
                tool_evidence=tuple(evidence),
                model_calls=records,
                handoff=handoff,
            )
        )


def build_analyst_workflow(
    provider: ToolEnabledStructuredModelProvider,
    connected_tools: ConnectedDataEngineerMCPTools,
    *,
    clock: Callable[[], UtcDateTime] | None = None,
) -> Workflow:
    executor = AutonomousAnalystExecutor(provider, connected_tools, clock=clock)
    return WorkflowBuilder(start_executor=executor, output_from=[executor]).build()
