"""Trusted boundary for pre-PM, read-only requirements discovery."""

from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
from math import ceil
from pathlib import Path

from pydantic import Field

from contracts import (
    AnalysisFact,
    AnalysisFactKind,
    Evidence,
    EvidenceKind,
    PMRequirementsHandoff,
    RequirementsAnalysisReport,
    TaskRequest,
    ToolCallEvidence,
    ToolCallStatus,
    ToolName,
)
from contracts.artifacts import RequiredTextTuple, TextTuple
from contracts.common import FrozenModel, Identifier, NonEmptyText, Sha256, UtcDateTime
from orchestrator import (
    BudgetCharge,
    BudgetLimits,
    Stage,
    TransitionCommand,
    WorkflowEvent,
    WorkflowState,
    append_transition,
    initial_state,
    verify_event_chain,
)
from policies import ToolUsage
from runtime.context import ContextBundle, build_scenario_context
from runtime.model_provider import ModelUsage
from runtime.scenario_harness import load_manifest

ANALYST_INSTRUCTIONS_PATH = Path(__file__).resolve().parents[1] / "agents/analyst/instructions.md"
ANALYST_READ_ONLY_TOOLS = frozenset(
    {
        ToolName.WORKSPACE_READ_FILE,
        ToolName.CLICKHOUSE_LIST_TABLES,
        ToolName.CLICKHOUSE_RUN_QUERY,
        ToolName.DBT_LIST,
        ToolName.DBT_GET_LINEAGE_DEV,
        ToolName.DBT_GET_NODE_DETAILS_DEV,
    }
)
ANALYST_PROFILE_SQL = """SELECT
    count() AS order_count,
    uniqExact(currency) AS currency_count,
    countIf(currency IS NULL OR empty(currency)) AS missing_currency_count,
    min(ordered_at) AS earliest_order_at,
    max(ordered_at) AS latest_order_at
FROM raw.orders
LIMIT 1"""


class AnalystBoundaryError(RuntimeError):
    """Discovery output or evidence failed the trusted boundary."""


class ObservedFactDraft(FrozenModel):
    kind: AnalysisFactKind
    statement: NonEmptyText


class AnalystPhaseDraft(FrozenModel):
    facts: tuple[ObservedFactDraft, ...] = Field(min_length=1, max_length=64)


class AnalystSynthesisDraft(FrozenModel):
    assumptions: TextTuple = ()
    open_questions: TextTuple = ()
    risks: TextTuple = ()
    recommended_next_steps: RequiredTextTuple


class AnalystRunRequest(FrozenModel):
    task: TaskRequest
    context: ContextBundle
    workflow_id: Identifier
    correlation_id: Identifier
    configuration_fingerprint: Sha256
    budget_limits: BudgetLimits
    agent_id: Identifier = "analyst-agent"


def _identifier(prefix: str, *parts: str) -> str:
    digest = sha256("\x00".join(parts).encode()).hexdigest()[:24]
    return f"{prefix}-{digest}"


def analyst_system_prompt() -> str:
    path = ANALYST_INSTRUCTIONS_PATH
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("Analyst instructions must be a regular repository file")
    contents = path.read_bytes()
    if not 1 <= len(contents) <= 12_000:
        raise RuntimeError("Analyst instructions exceed the trusted size boundary")
    try:
        result = contents.decode("utf-8").strip()
    except UnicodeDecodeError:
        raise RuntimeError("Analyst instructions must be UTF-8") from None
    if not result:
        raise RuntimeError("Analyst instructions must not be empty")
    return result


def analyst_user_prompt(request: AnalystRunRequest) -> str:
    return (
        "Discover data facts needed before PM specification. Identity, evidence and transitions "
        "are code-owned.\n"
        f"<immutable_task>{request.task.model_dump_json(exclude={'evidence'})}</immutable_task>\n"
        f'<untrusted_context fingerprint="{request.context.workspace_fingerprint}">\n'
        f"{request.context.as_prompt()}\n</untrusted_context>"
    )


def prepare_analyst_request(
    repository_root: Path,
    scenario_id: str,
    *,
    workflow_id: str,
    correlation_id: str,
    configuration_fingerprint: Sha256,
    created_at: UtcDateTime | None = None,
    requested_state_root: Path | None = None,
) -> AnalystRunRequest:
    manifest = load_manifest(repository_root, scenario_id)
    context = build_scenario_context(
        repository_root,
        scenario_id,
        requested_state_root=requested_state_root,
    )
    timestamp = created_at or datetime.now(UTC)
    task_id = f"scenario-{manifest.scenario_id}"
    return AnalystRunRequest(
        task=TaskRequest(
            artifact_id=_identifier("request", workflow_id, task_id),
            task_id=task_id,
            producer_id="user",
            created_at=timestamp,
            title=f"Scenario {manifest.scenario_id}",
            description="Discover requirements and data constraints before PM specification.",
        ),
        context=context,
        workflow_id=workflow_id,
        correlation_id=correlation_id,
        configuration_fingerprint=configuration_fingerprint,
        budget_limits=BudgetLimits(**manifest.budgets),
    )


def seed_analyst_state(
    request: AnalystRunRequest,
    *,
    occurred_at: UtcDateTime,
) -> tuple[WorkflowState, tuple[WorkflowEvent, ...]]:
    if request.agent_id in {request.task.producer_id, "workflow", "pm-agent"}:
        raise AnalystBoundaryError("Analyst identity must be separate from user, workflow, and PM")
    state = initial_state(
        request.task,
        workflow_id=request.workflow_id,
        correlation_id=request.correlation_id,
        limits=request.budget_limits,
    )
    return append_transition(
        state,
        TransitionCommand(
            command_id=_identifier("cmd", request.workflow_id, "analyzing"),
            task_id=request.task.task_id,
            actor_id="workflow",
            target_stage=Stage.ANALYZING,
            occurred_at=occurred_at,
        ),
        (),
    )


def _domain_evidence(item: ToolCallEvidence) -> Evidence:
    if item.status is not ToolCallStatus.SUCCESS or item.output is None:
        raise AnalystBoundaryError("Analyst evidence contains a non-success tool outcome")
    if item.tool not in ANALYST_READ_ONLY_TOOLS:
        raise AnalystBoundaryError("Analyst evidence contains a non-read-only tool")
    kind = (
        EvidenceKind.QUERY
        if item.tool is ToolName.CLICKHOUSE_RUN_QUERY
        else EvidenceKind.ARTIFACT
        if item.tool is ToolName.WORKSPACE_READ_FILE
        else EvidenceKind.COMMAND
    )
    return Evidence(
        evidence_id=item.evidence_id,
        task_id=item.task_id,
        producer_id=item.producer_id,
        kind=kind,
        source=item.tool.value,
        invocation=f"arguments_sha256={item.arguments_sha256}",
        exit_code=0,
        artifact=item.output,
        occurred_at=item.completed_at,
    )


def accept_analyst_drafts(
    request: AnalystRunRequest,
    state: WorkflowState,
    events: tuple[WorkflowEvent, ...],
    phases: tuple[AnalystPhaseDraft, ...],
    synthesis: AnalystSynthesisDraft,
    *,
    phase_evidence: tuple[ToolCallEvidence, ...],
    phase_outputs: tuple[str, ...],
    tool_usage: ToolUsage,
    model_usage: ModelUsage,
    model_latency_ms: int,
    completed_at: UtcDateTime,
) -> tuple[RequirementsAnalysisReport, WorkflowState, tuple[WorkflowEvent, ...]]:
    if state.stage is not Stage.ANALYZING:
        raise AnalystBoundaryError("Analyst requires analyzing state")
    if state.task_id != request.task.task_id or state.workflow_id != request.workflow_id:
        raise AnalystBoundaryError("Analyst request belongs to another workflow or task")
    if len(phases) != len(phase_evidence) or len(phases) != len(phase_outputs) or not phases:
        raise AnalystBoundaryError("each discovery phase requires exactly one evidence item")
    if any(item.task_id != state.task_id for item in phase_evidence):
        raise AnalystBoundaryError("Analyst evidence belongs to another task")
    evidence = tuple(_domain_evidence(item) for item in phase_evidence)
    allowed_kinds = (
        frozenset({AnalysisFactKind.SOURCE, AnalysisFactKind.MODEL}),
        frozenset({AnalysisFactKind.LINEAGE}),
        frozenset({AnalysisFactKind.PROFILE}),
    )
    if len(phases) != len(allowed_kinds) or any(
        fact.kind not in allowed_kinds[index]
        for index, phase in enumerate(phases)
        for fact in phase.facts
    ):
        raise AnalystBoundaryError("discovery phase returned a fact outside its owned category")
    if any(
        fact.statement not in phase_outputs[index]
        for index, phase in enumerate(phases)
        for fact in phase.facts
    ):
        raise AnalystBoundaryError("analysis fact is not an exact excerpt of its tool observation")
    if any(item.occurred_at > completed_at for item in evidence):
        raise AnalystBoundaryError("analysis completion predates evidence")
    facts = tuple(
        AnalysisFact(
            fact_id=_identifier("fact", request.workflow_id, str(phase_index), str(fact_index)),
            kind=fact.kind,
            statement=fact.statement,
            evidence_ids=(phase_evidence[phase_index].evidence_id,),
        )
        for phase_index, phase in enumerate(phases)
        for fact_index, fact in enumerate(phase.facts)
    )
    report = RequirementsAnalysisReport(
        artifact_id=_identifier("requirements-analysis", request.workflow_id, state.task_id),
        task_id=state.task_id,
        producer_id=request.agent_id,
        created_at=completed_at,
        facts=facts,
        assumptions=synthesis.assumptions,
        open_questions=synthesis.open_questions,
        risks=synthesis.risks,
        recommended_next_steps=synthesis.recommended_next_steps,
        evidence=evidence,
    )
    state, events = append_transition(
        state,
        TransitionCommand(
            command_id=_identifier("cmd", request.workflow_id, "analysis-ready"),
            task_id=state.task_id,
            actor_id=request.agent_id,
            target_stage=Stage.ANALYSIS_READY,
            occurred_at=completed_at,
            artifact=report,
            charge=BudgetCharge(
                tool_calls=tool_usage.completed_calls,
                model_tokens=model_usage.total_tokens,
                wall_time_seconds=ceil(max(model_latency_ms, tool_usage.elapsed_ms) / 1_000),
            ),
        ),
        events,
    )
    verify_event_chain(events, expected_state=state)
    return report, state, events


def build_pm_requirements_handoff(
    request: AnalystRunRequest,
    report: RequirementsAnalysisReport,
    state: WorkflowState,
) -> PMRequirementsHandoff:
    """Build PM input only from the report accepted by this workflow."""

    if state.stage is not Stage.ANALYSIS_READY:
        raise AnalystBoundaryError("PM handoff requires analysis_ready state")
    if state.workflow_id != request.workflow_id or state.task_id != request.task.task_id:
        raise AnalystBoundaryError("PM handoff belongs to another workflow or task")
    if report.task_id != state.task_id or report.artifact_id not in state.artifact_ids:
        raise AnalystBoundaryError("PM handoff requires the accepted analysis artifact")
    return PMRequirementsHandoff(
        workflow_id=state.workflow_id,
        task=request.task,
        analysis=report,
        unresolved_questions=report.open_questions,
        configuration_fingerprint=request.configuration_fingerprint,
    )
