"""Trusted boundary for the independent read-only Reviewer role."""

from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
from math import ceil
from pathlib import Path
from typing import Self

from pydantic import Field, model_validator

from contracts import (
    CriterionAssessment,
    CriterionStatus,
    Evidence,
    EvidenceKind,
    QADecision,
    QAReport,
    ReviewDecision,
    ReviewFinding,
    ReviewReport,
    ScenarioSpecification,
    Severity,
    ToolCallEvidence,
    ToolCallStatus,
    ToolName,
)
from contracts.artifacts import TextTuple
from contracts.common import FrozenModel, Identifier, NonEmptyText, ShortText, UtcDateTime
from orchestrator import (
    BudgetCharge,
    Stage,
    TransitionCommand,
    WorkflowEvent,
    WorkflowState,
    append_transition,
    verify_event_chain,
)
from policies import ToolUsage
from runtime.context import ContextBundle, build_scenario_context
from runtime.model_provider import ModelUsage
from runtime.specification import load_scenario_specification

REVIEWER_INSTRUCTIONS_PATH = Path(__file__).resolve().parents[1] / "agents/reviewer/instructions.md"
REVIEWER_CONTEXT_PATHS = (
    "TASK.md",
    "platform/dbt/models/marts/fct_net_revenue.sql",
    "platform/dbt/tests/assert_fct_net_revenue_contract.sql",
)
REVIEWER_READ_ONLY_TOOLS = frozenset({ToolName.WORKSPACE_READ_FILE})


class ReviewerBoundaryError(RuntimeError):
    """Untrusted Reviewer output or evidence crossed the role boundary."""


class ReviewerInspectionDraft(FrozenModel):
    observations: tuple[NonEmptyText, ...] = Field(min_length=1, max_length=32)
    findings: tuple[NonEmptyText, ...] = Field(max_length=32)
    risks: TextTuple = ()


class ReviewerCriterionDraft(FrozenModel):
    criterion: ShortText
    status: CriterionStatus
    rationale: NonEmptyText


class ReviewerFindingDraft(FrozenModel):
    severity: Severity
    description: NonEmptyText
    acceptance_criterion: ShortText


class ReviewerDraft(FrozenModel):
    decision: ReviewDecision
    acceptance_criteria: tuple[ReviewerCriterionDraft, ...] = Field(min_length=1, max_length=64)
    findings: tuple[ReviewerFindingDraft, ...] = Field(max_length=32, default=())
    risks: TextTuple = ()
    summary: NonEmptyText

    @model_validator(mode="after")
    def validate_decision_shape(self) -> Self:
        statuses = {item.status for item in self.acceptance_criteria}
        blocking = any(
            item.severity in {Severity.HIGH, Severity.CRITICAL} for item in self.findings
        )
        if self.decision is ReviewDecision.APPROVE:
            if statuses != {CriterionStatus.PASS} or blocking:
                raise ValueError(
                    "approval draft requires all criteria pass and no blocking finding"
                )
        elif self.decision is ReviewDecision.REQUEST_CHANGES:
            if CriterionStatus.FAIL not in statuses and not self.findings:
                raise ValueError("request_changes draft requires a failed criterion or finding")
        elif CriterionStatus.NOT_ASSESSED not in statuses:
            raise ValueError("blocked draft requires a not_assessed criterion")
        return self


class ReviewerRunRequest(FrozenModel):
    specification: ScenarioSpecification
    context: ContextBundle
    qa_report: QAReport
    workflow_id: Identifier
    agent_id: Identifier = "reviewer-agent"


def _identifier(prefix: str, *parts: str) -> str:
    digest = sha256("\x00".join(parts).encode()).hexdigest()[:24]
    return f"{prefix}-{digest}"


def reviewer_system_prompt() -> str:
    path = REVIEWER_INSTRUCTIONS_PATH
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("Reviewer instructions must be a regular repository file")
    contents = path.read_bytes()
    if not 1 <= len(contents) <= 12_000:
        raise RuntimeError("Reviewer instructions exceed the trusted size boundary")
    try:
        instructions = contents.decode("utf-8").strip()
    except UnicodeDecodeError:
        raise RuntimeError("Reviewer instructions must be UTF-8") from None
    if not instructions:
        raise RuntimeError("Reviewer instructions must not be empty")
    return instructions


def reviewer_user_prompt(request: ReviewerRunRequest) -> str:
    specification = request.specification.specification.model_dump_json(exclude={"evidence"})
    qa_report = request.qa_report.model_dump_json(
        exclude={"evidence": {"__all__": {"artifact": {"path"}}}}
    )
    return (
        "Review this QA-passed candidate and return only the requested structured draft.\n"
        f"<immutable_specification>{specification}</immutable_specification>\n"
        f"<accepted_qa_report>{qa_report}</accepted_qa_report>\n"
        f'<untrusted_candidate_context fingerprint="{request.context.workspace_fingerprint}">\n'
        f"{request.context.as_prompt()}\n"
        "</untrusted_candidate_context>"
    )


def prepare_reviewer_request(
    repository_root: Path,
    scenario_id: str,
    *,
    workflow_id: str,
    qa_report: QAReport,
    requested_state_root: Path | None = None,
) -> ReviewerRunRequest:
    specification = load_scenario_specification(
        repository_root,
        scenario_id,
        requested_state_root=requested_state_root,
    )
    context = build_scenario_context(
        repository_root,
        scenario_id,
        relative_paths=REVIEWER_CONTEXT_PATHS,
        requested_state_root=requested_state_root,
    )
    return ReviewerRunRequest(
        specification=specification,
        context=context,
        qa_report=qa_report,
        workflow_id=workflow_id,
    )


def _domain_evidence(item: ToolCallEvidence) -> Evidence:
    if item.status is not ToolCallStatus.SUCCESS or item.output is None:
        raise ReviewerBoundaryError("Reviewer evidence contains a non-success tool outcome")
    if item.tool not in REVIEWER_READ_ONLY_TOOLS:
        raise ReviewerBoundaryError("Reviewer evidence contains a non-read-only tool")
    return Evidence(
        evidence_id=item.evidence_id,
        task_id=item.task_id,
        producer_id=item.producer_id,
        kind=EvidenceKind.ARTIFACT,
        source=item.tool.value,
        invocation=f"arguments_sha256={item.arguments_sha256}",
        exit_code=0,
        artifact=item.output,
        occurred_at=item.completed_at,
    )


def accept_reviewer_draft(
    request: ReviewerRunRequest,
    state: WorkflowState,
    events: tuple[WorkflowEvent, ...],
    draft: ReviewerDraft,
    *,
    tool_evidence: tuple[ToolCallEvidence, ...],
    tool_usage: ToolUsage,
    model_usage: ModelUsage,
    model_latency_ms: int,
    completed_at: UtcDateTime | None = None,
) -> tuple[ReviewReport, WorkflowState, tuple[WorkflowEvent, ...]]:
    if state.stage is not Stage.QA_PASSED:
        raise ReviewerBoundaryError("Reviewer requires a QA-passed workflow state")
    if state.implementation_author_id is None:
        raise ReviewerBoundaryError("Reviewer requires an implementation author")
    if request.workflow_id != state.workflow_id:
        raise ReviewerBoundaryError("Reviewer request belongs to another workflow")
    if request.specification.specification.task_id != state.task_id:
        raise ReviewerBoundaryError("Reviewer specification belongs to another task")
    if request.qa_report.task_id != state.task_id:
        raise ReviewerBoundaryError("Reviewer QA report belongs to another task")
    if request.qa_report.decision is not QADecision.PASS:
        raise ReviewerBoundaryError("Reviewer requires an accepted passing QA report")
    if request.qa_report.artifact_id not in state.artifact_ids:
        raise ReviewerBoundaryError("Reviewer QA report was not accepted by this workflow")
    if request.qa_report.implementation_author_id != state.implementation_author_id:
        raise ReviewerBoundaryError("Reviewer QA report references another implementation")
    if request.agent_id in {
        state.implementation_author_id,
        request.qa_report.producer_id,
    }:
        raise ReviewerBoundaryError("Reviewer identity must be independent from DE and QA")
    if not tool_evidence or any(item.task_id != state.task_id for item in tool_evidence):
        raise ReviewerBoundaryError("Reviewer requires same-task measured evidence")

    expected_criteria = tuple(request.specification.specification.acceptance_criteria)
    actual_criteria = tuple(item.criterion for item in draft.acceptance_criteria)
    if len(actual_criteria) != len(set(actual_criteria)):
        raise ReviewerBoundaryError("Reviewer criteria must not contain duplicates")
    if set(actual_criteria) != set(expected_criteria):
        raise ReviewerBoundaryError("Reviewer must assess every immutable criterion exactly once")
    if any(item.acceptance_criterion not in set(expected_criteria) for item in draft.findings):
        raise ReviewerBoundaryError("Reviewer finding references an unknown criterion")

    measured = tuple(_domain_evidence(item) for item in tool_evidence)
    finished_at = completed_at or datetime.now(UTC)
    if any(item.occurred_at > finished_at for item in measured):
        raise ReviewerBoundaryError("Review report predates its evidence")
    evidence_ids = tuple(item.evidence_id for item in measured)
    criterion_drafts = {item.criterion: item for item in draft.acceptance_criteria}
    report = ReviewReport(
        artifact_id=_identifier("review-report", request.workflow_id, str(state.revision)),
        task_id=state.task_id,
        producer_id=request.agent_id,
        created_at=finished_at,
        implementation_author_id=state.implementation_author_id,
        decision=draft.decision,
        findings=tuple(
            ReviewFinding(
                finding_id=_identifier(
                    "review-finding", request.workflow_id, str(state.revision), str(index)
                ),
                severity=item.severity,
                description=item.description,
                acceptance_criterion=item.acceptance_criterion,
                evidence_ids=evidence_ids,
            )
            for index, item in enumerate(draft.findings)
        ),
        acceptance_criteria=tuple(
            CriterionAssessment(
                criterion_id=_identifier(
                    "criterion", request.workflow_id, str(state.revision), str(index)
                ),
                status=criterion_drafts[criterion].status,
                rationale=criterion_drafts[criterion].rationale,
                evidence_ids=evidence_ids,
            )
            for index, criterion in enumerate(expected_criteria)
        ),
        risks=draft.risks,
        summary=draft.summary,
        evidence=measured,
    )
    state, events = append_transition(
        state,
        TransitionCommand(
            command_id=_identifier("cmd", request.workflow_id, str(state.revision), "review-start"),
            task_id=state.task_id,
            actor_id=request.agent_id,
            target_stage=Stage.REVIEW,
            occurred_at=finished_at,
        ),
        events,
    )
    target = {
        ReviewDecision.APPROVE: Stage.DONE,
        ReviewDecision.REQUEST_CHANGES: Stage.REWORK,
        ReviewDecision.BLOCKED: Stage.BLOCKED,
    }[draft.decision]
    reason = draft.summary if target in {Stage.REWORK, Stage.BLOCKED} else None
    tool_duration_ms = max(tool_usage.elapsed_ms, sum(item.duration_ms for item in tool_evidence))
    state, events = append_transition(
        state,
        TransitionCommand(
            command_id=_identifier(
                "cmd", request.workflow_id, str(state.revision), "review-result"
            ),
            task_id=state.task_id,
            actor_id=request.agent_id,
            target_stage=target,
            occurred_at=finished_at,
            artifact=report,
            charge=BudgetCharge(
                tool_calls=tool_usage.completed_calls,
                model_tokens=model_usage.total_tokens,
                wall_time_seconds=ceil(max(model_latency_ms, tool_duration_ms) / 1_000),
                rework_attempts=1 if target is Stage.REWORK else 0,
            ),
            reason=reason,
        ),
        events,
    )
    verify_event_chain(events, expected_state=state)
    return report, state, events
