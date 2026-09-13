"""Trusted request boundary for the autonomous Data Engineer role."""

from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
from math import ceil
from pathlib import Path

from pydantic import model_validator

from contracts import (
    AnalysisFact,
    AnalysisFactKind,
    AnalysisReport,
    ArtifactReference,
    Evidence,
    EvidenceKind,
    ImplementationResult,
    ImplementationStatus,
    RequirementsAnalysisReport,
    ScenarioSpecification,
    TaskRequest,
    ToolCallEvidence,
    ToolCallStatus,
    ToolName,
)
from contracts.artifacts import RequiredTextTuple, TextTuple
from contracts.common import FrozenModel, Identifier, NonEmptyText, UtcDateTime
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
from runtime.specification import load_scenario_specification

DATA_ENGINEER_INSTRUCTIONS_PATH = (
    Path(__file__).resolve().parents[1] / "agents/data_engineer/instructions.md"
)
DATA_ENGINEER_CONTEXT_PATHS = (
    "TASK.md",
    "platform/dbt/models/intermediate/int_order_payments.sql",
    "platform/dbt/models/intermediate/int_order_refunds.sql",
    "platform/dbt/models/marts/fct_orders.sql",
    "platform/dbt/models/staging/sources.yml",
)


class DataEngineerBoundaryError(RuntimeError):
    """Measured execution facts cannot form valid Data Engineer artifacts."""


class DataEngineerDraft(FrozenModel):
    """Untrusted role output without control-plane identity or evidence fields."""

    relevant_sources: RequiredTextTuple
    findings: RequiredTextTuple
    recommended_approach: NonEmptyText
    status: ImplementationStatus
    summary: NonEmptyText
    semantic_risks: TextTuple = ()
    known_issues: TextTuple = ()

    @model_validator(mode="after")
    def validate_outcome(self):
        if self.status in {ImplementationStatus.BLOCKED, ImplementationStatus.FAILED}:
            if not self.known_issues:
                raise ValueError("blocked or failed draft requires known issues")
        return self


class DataEngineerInvestigationDraft(FrozenModel):
    """Minimal untrusted output for the read-only investigation phase."""

    relevant_sources: RequiredTextTuple
    findings: RequiredTextTuple
    recommended_approach: NonEmptyText
    semantic_risks: TextTuple = ()


class DataEngineerImplementationDraft(FrozenModel):
    """Minimal untrusted output after one implementation or repair write."""

    status: ImplementationStatus
    summary: NonEmptyText
    known_issues: TextTuple = ()

    @model_validator(mode="after")
    def validate_outcome(self):
        if self.status in {ImplementationStatus.BLOCKED, ImplementationStatus.FAILED}:
            if not self.known_issues:
                raise ValueError("blocked or failed draft requires known issues")
        return self


class DataEngineerRunRequest(FrozenModel):
    specification: ScenarioSpecification
    context: ContextBundle
    workflow_id: Identifier
    correlation_id: Identifier
    started_at: UtcDateTime
    agent_id: Identifier = "data-engineer-agent"
    budget_limits: BudgetLimits


def _identifier(prefix: str, *parts: str) -> str:
    digest = sha256("\x00".join(parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}-{digest}"


def data_engineer_system_prompt() -> str:
    """Load bounded trusted role instructions from the repository checkout."""

    path = DATA_ENGINEER_INSTRUCTIONS_PATH
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("Data Engineer instructions must be a regular repository file")
    contents = path.read_bytes()
    if not 1 <= len(contents) <= 12_000:
        raise RuntimeError("Data Engineer instructions exceed the trusted size boundary")
    try:
        instructions = contents.decode("utf-8").strip()
    except UnicodeDecodeError:
        raise RuntimeError("Data Engineer instructions must be UTF-8") from None
    if not instructions:
        raise RuntimeError("Data Engineer instructions must not be empty")
    return instructions


def data_engineer_specification_prompt(request: DataEngineerRunRequest) -> str:
    """Render the immutable specification without repeating workspace context."""

    specification = request.specification.specification.model_dump_json(exclude={"evidence"})
    return (
        "Implement this immutable human-authored specification. Use tools to inspect, edit, and "
        "self-check the disposable workspace. Return only the requested structured draft.\n"
        f"<immutable_specification>{specification}</immutable_specification>"
    )


def data_engineer_user_prompt(request: DataEngineerRunRequest) -> str:
    """Render immutable spec separately from explicitly untrusted context."""

    return (
        f"{data_engineer_specification_prompt(request)}\n"
        f'<untrusted_workspace_context fingerprint="{request.context.workspace_fingerprint}">\n'
        f"{request.context.as_prompt()}\n"
        "</untrusted_workspace_context>"
    )


def prepare_data_engineer_request(
    repository_root: Path,
    scenario_id: str,
    *,
    workflow_id: str,
    correlation_id: str,
    started_at: UtcDateTime | None = None,
    requested_state_root: Path | None = None,
) -> DataEngineerRunRequest:
    """Build a DE request only from one verified scenario workspace and frozen spec."""

    manifest = load_manifest(repository_root, scenario_id)
    specification = load_scenario_specification(
        repository_root,
        scenario_id,
        requested_state_root=requested_state_root,
    )
    context = build_scenario_context(
        repository_root,
        scenario_id,
        relative_paths=DATA_ENGINEER_CONTEXT_PATHS,
        requested_state_root=requested_state_root,
    )
    return DataEngineerRunRequest(
        specification=specification,
        context=context,
        workflow_id=workflow_id,
        correlation_id=correlation_id,
        started_at=started_at or datetime.now(UTC),
        budget_limits=BudgetLimits(**manifest.budgets),
    )


def seed_data_engineer_state(
    request: DataEngineerRunRequest,
) -> tuple[WorkflowState, tuple[WorkflowEvent, ...]]:
    """Accept an attested human discovery and specification, then enter implementation."""

    task_id = request.specification.specification.task_id
    task = TaskRequest(
        artifact_id=_identifier("request", request.workflow_id, task_id),
        task_id=task_id,
        producer_id="user",
        created_at=request.started_at,
        title=f"Autonomous scenario {request.specification.scenario_id}",
        description="Implement the frozen human-authored scenario specification.",
    )
    state = initial_state(
        task,
        workflow_id=request.workflow_id,
        correlation_id=request.correlation_id,
        limits=request.budget_limits,
    )
    events: tuple[WorkflowEvent, ...] = ()
    discovery_evidence = Evidence(
        evidence_id=_identifier("evidence", request.workflow_id, "human-task"),
        task_id=task_id,
        producer_id="human",
        kind=EvidenceKind.ARTIFACT,
        source="scenario-task",
        invocation=f"task_sha256={request.specification.task_sha256}",
        exit_code=0,
        artifact=ArtifactReference(
            path=f"scenarios/{request.specification.scenario_id}/TASK.md",
            sha256=request.specification.task_sha256,
            media_type="text/markdown",
            size_bytes=0,
        ),
        occurred_at=request.started_at,
    )
    discovery = RequirementsAnalysisReport(
        artifact_id=_identifier("requirements-analysis", request.workflow_id, "human"),
        task_id=task_id,
        producer_id="human",
        created_at=request.started_at,
        facts=(
            AnalysisFact(
                fact_id=_identifier("fact", request.workflow_id, "human-spec"),
                kind=AnalysisFactKind.SEMANTIC,
                statement="A frozen human-authored scenario specification is available.",
                evidence_ids=(discovery_evidence.evidence_id,),
            ),
        ),
        assumptions=request.specification.specification.assumptions,
        open_questions=(),
        risks=request.specification.specification.risks,
        recommended_next_steps=("Implement the accepted human specification.",),
        evidence=(discovery_evidence,),
    )
    transitions = (
        TransitionCommand(
            command_id=_identifier("cmd", request.workflow_id, "analyzing"),
            task_id=task_id,
            actor_id="workflow",
            target_stage=Stage.ANALYZING,
            occurred_at=request.started_at,
        ),
        TransitionCommand(
            command_id=_identifier("cmd", request.workflow_id, "analysis-ready"),
            task_id=task_id,
            actor_id="human",
            target_stage=Stage.ANALYSIS_READY,
            occurred_at=request.started_at,
            artifact=discovery,
        ),
        TransitionCommand(
            command_id=_identifier("cmd", request.workflow_id, "specifying"),
            task_id=task_id,
            actor_id="workflow",
            target_stage=Stage.SPECIFYING,
            occurred_at=request.started_at,
        ),
        TransitionCommand(
            command_id=_identifier("cmd", request.workflow_id, "spec-ready"),
            task_id=task_id,
            actor_id="human",
            target_stage=Stage.SPEC_READY,
            occurred_at=request.started_at,
            artifact=request.specification.specification,
        ),
        TransitionCommand(
            command_id=_identifier("cmd", request.workflow_id, "implementing"),
            task_id=task_id,
            actor_id="workflow",
            target_stage=Stage.IMPLEMENTING,
            occurred_at=request.started_at,
        ),
    )
    for transition in transitions:
        state, events = append_transition(state, transition, events)
    verify_event_chain(events, expected_state=state)
    return state, events


def _domain_evidence(item: ToolCallEvidence) -> Evidence:
    if item.status is not ToolCallStatus.SUCCESS or item.output is None:
        raise DataEngineerBoundaryError("Data Engineer run contains a non-success tool outcome")
    if item.tool is ToolName.CLICKHOUSE_RUN_QUERY:
        kind = EvidenceKind.QUERY
    elif item.tool in {ToolName.DBT_BUILD, ToolName.DBT_TEST}:
        kind = EvidenceKind.TEST
    elif item.tool in {ToolName.WORKSPACE_READ_FILE, ToolName.WORKSPACE_WRITE_FILE}:
        kind = EvidenceKind.ARTIFACT
    else:
        kind = EvidenceKind.COMMAND
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


def accept_data_engineer_draft(
    request: DataEngineerRunRequest,
    state: WorkflowState,
    events: tuple[WorkflowEvent, ...],
    draft: DataEngineerDraft,
    *,
    tool_evidence: tuple[ToolCallEvidence, ...],
    tool_usage: ToolUsage,
    model_usage: ModelUsage,
    model_latency_ms: int,
    changed_files: tuple[str, ...],
    completed_at: UtcDateTime,
) -> tuple[AnalysisReport, ImplementationResult, WorkflowState, tuple[WorkflowEvent, ...]]:
    """Assemble code-owned artifacts and accept them through deterministic gates."""

    if state.stage is not Stage.IMPLEMENTING:
        raise DataEngineerBoundaryError("Data Engineer draft requires implementing state")
    if any(item.task_id != state.task_id for item in tool_evidence):
        raise DataEngineerBoundaryError("tool evidence belongs to another task")
    measured = tuple(_domain_evidence(item) for item in tool_evidence)
    analysis_evidence = tuple(
        evidence
        for evidence, raw in zip(measured, tool_evidence, strict=True)
        if raw.tool is not ToolName.WORKSPACE_WRITE_FILE
    )
    if not analysis_evidence:
        raise DataEngineerBoundaryError("analysis requires measured non-write evidence")
    if not measured:
        raise DataEngineerBoundaryError("implementation requires measured evidence")
    if any(item.occurred_at > completed_at for item in measured):
        raise DataEngineerBoundaryError("artifact completion predates tool evidence")

    attempt = str(state.revision)
    analysis = AnalysisReport(
        artifact_id=_identifier("analysis", request.workflow_id, attempt),
        task_id=state.task_id,
        producer_id=request.agent_id,
        created_at=completed_at,
        relevant_sources=draft.relevant_sources,
        findings=draft.findings,
        recommended_approach=draft.recommended_approach,
        semantic_risks=draft.semantic_risks,
        evidence=analysis_evidence,
    )
    normalized_changes = tuple(sorted(set(changed_files)))
    effective_status = draft.status
    known_issues = draft.known_issues
    if effective_status is ImplementationStatus.COMPLETED and not normalized_changes:
        effective_status = ImplementationStatus.FAILED
        known_issues = (*known_issues, "control plane observed no changed dbt files")
    tests_executed = tuple(
        item.evidence_id
        for item in tool_evidence
        if item.tool in {ToolName.DBT_BUILD, ToolName.DBT_TEST}
    )
    implementation = ImplementationResult(
        artifact_id=_identifier("implementation", request.workflow_id, attempt),
        task_id=state.task_id,
        producer_id=request.agent_id,
        created_at=completed_at,
        status=effective_status,
        changed_files=normalized_changes,
        summary=draft.summary,
        tests_executed=tests_executed,
        known_issues=known_issues,
        evidence=measured,
    )
    wall_time_seconds = ceil(max(model_latency_ms, tool_usage.elapsed_ms) / 1_000)
    target = {
        ImplementationStatus.COMPLETED: Stage.IMPLEMENTED,
        ImplementationStatus.BLOCKED: Stage.BLOCKED,
        ImplementationStatus.FAILED: Stage.FAILED,
    }[implementation.status]
    reason = None
    if target in {Stage.BLOCKED, Stage.FAILED}:
        reason = "; ".join(implementation.known_issues)
    state, events = append_transition(
        state,
        TransitionCommand(
            command_id=_identifier("cmd", request.workflow_id, attempt, "implementation-result"),
            task_id=state.task_id,
            actor_id=request.agent_id,
            target_stage=target,
            occurred_at=completed_at,
            artifact=implementation,
            charge={
                "tool_calls": tool_usage.completed_calls,
                "model_tokens": model_usage.total_tokens,
                "wall_time_seconds": wall_time_seconds,
            },
            reason=reason,
        ),
        events,
    )
    verify_event_chain(events, expected_state=state)
    return analysis, implementation, state, events


def accept_data_engineer_rework(
    request: DataEngineerRunRequest,
    state: WorkflowState,
    events: tuple[WorkflowEvent, ...],
    draft: DataEngineerDraft,
    *,
    tool_evidence: tuple[ToolCallEvidence, ...],
    model_usage: ModelUsage,
    model_latency_ms: int,
    changed_files: tuple[str, ...],
    completed_at: UtcDateTime,
) -> tuple[ImplementationResult, WorkflowState, tuple[WorkflowEvent, ...]]:
    """Accept one measured repair without recreating the original analysis artifact."""

    if state.stage is not Stage.REWORK:
        raise DataEngineerBoundaryError("Data Engineer repair requires rework state")
    if any(item.task_id != state.task_id for item in tool_evidence):
        raise DataEngineerBoundaryError("repair evidence belongs to another task")
    measured = tuple(_domain_evidence(item) for item in tool_evidence)
    if not measured or not any(
        item.tool is ToolName.WORKSPACE_WRITE_FILE for item in tool_evidence
    ):
        raise DataEngineerBoundaryError("repair requires measured workspace write evidence")
    normalized_changes = tuple(sorted(set(changed_files)))
    effective_status = draft.status
    known_issues = draft.known_issues
    if effective_status is ImplementationStatus.COMPLETED and not normalized_changes:
        effective_status = ImplementationStatus.FAILED
        known_issues = (*known_issues, "control plane observed no changed dbt files")
    implementation = ImplementationResult(
        artifact_id=_identifier(
            "implementation", request.workflow_id, str(state.revision), "rework"
        ),
        task_id=state.task_id,
        producer_id=request.agent_id,
        created_at=completed_at,
        status=effective_status,
        changed_files=normalized_changes,
        summary=draft.summary,
        known_issues=known_issues,
        evidence=measured,
    )
    state, events = append_transition(
        state,
        TransitionCommand(
            command_id=_identifier("cmd", request.workflow_id, str(state.revision), "rework-start"),
            task_id=state.task_id,
            actor_id=request.agent_id,
            target_stage=Stage.IMPLEMENTING,
            occurred_at=completed_at,
        ),
        events,
    )
    target = {
        ImplementationStatus.COMPLETED: Stage.IMPLEMENTED,
        ImplementationStatus.BLOCKED: Stage.BLOCKED,
        ImplementationStatus.FAILED: Stage.FAILED,
    }[implementation.status]
    reason = None
    if target in {Stage.BLOCKED, Stage.FAILED}:
        reason = "; ".join(implementation.known_issues)
    tool_duration_ms = sum(item.duration_ms for item in tool_evidence)
    state, events = append_transition(
        state,
        TransitionCommand(
            command_id=_identifier(
                "cmd", request.workflow_id, str(state.revision), "rework-result"
            ),
            task_id=state.task_id,
            actor_id=request.agent_id,
            target_stage=target,
            occurred_at=completed_at,
            artifact=implementation,
            charge=BudgetCharge(
                tool_calls=len(tool_evidence),
                model_tokens=model_usage.total_tokens,
                wall_time_seconds=ceil(max(model_latency_ms, tool_duration_ms) / 1_000),
            ),
            reason=reason,
        ),
        events,
    )
    verify_event_chain(events, expected_state=state)
    return implementation, state, events
