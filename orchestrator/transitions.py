"""Pure, code-owned transition reducer and artifact gates."""

from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator

from contracts import (
    AnalysisReport,
    Artifact,
    ImplementationResult,
    ImplementationStatus,
    QADecision,
    QAReport,
    ReviewDecision,
    ReviewReport,
    SpecificationDecision,
    TaskSpecification,
    ValidationDecision,
    ValidationResult,
)
from contracts.artifacts import ArtifactBase
from contracts.common import Identifier, NonEmptyText, UtcDateTime, VersionedModel
from orchestrator.errors import ArtifactGateError, IllegalTransitionError
from orchestrator.state import BudgetCharge, BudgetState, Stage, WorkflowState

ALLOWED_TRANSITIONS: dict[Stage, frozenset[Stage]] = {
    Stage.CREATED: frozenset({Stage.SPECIFYING}),
    Stage.SPECIFYING: frozenset({Stage.SPEC_READY, Stage.BLOCKED}),
    Stage.SPEC_READY: frozenset({Stage.ANALYZING}),
    Stage.ANALYZING: frozenset({Stage.ANALYSIS_READY}),
    Stage.ANALYSIS_READY: frozenset({Stage.IMPLEMENTING}),
    Stage.IMPLEMENTING: frozenset({Stage.IMPLEMENTED, Stage.BLOCKED, Stage.FAILED}),
    Stage.IMPLEMENTED: frozenset({Stage.VALIDATING}),
    Stage.VALIDATING: frozenset({Stage.VALIDATED, Stage.REWORK, Stage.FAILED}),
    Stage.VALIDATED: frozenset({Stage.QA}),
    Stage.QA: frozenset({Stage.QA_PASSED, Stage.REWORK, Stage.BLOCKED}),
    Stage.QA_PASSED: frozenset({Stage.REVIEW}),
    Stage.REVIEW: frozenset({Stage.DONE, Stage.REWORK, Stage.BLOCKED}),
    Stage.REWORK: frozenset({Stage.IMPLEMENTING}),
    Stage.DONE: frozenset(),
    Stage.BLOCKED: frozenset(),
    Stage.FAILED: frozenset(),
}


class TransitionCommand(VersionedModel):
    """An orchestrator-created request; it is never a role output contract."""

    command_id: Identifier
    task_id: Identifier
    actor_id: Identifier
    target_stage: Stage
    occurred_at: UtcDateTime
    artifact: Artifact | None = None
    charge: BudgetCharge = Field(default_factory=BudgetCharge)
    reason: NonEmptyText | None = None

    @model_validator(mode="after")
    def validate_reason_and_rework_charge(self) -> Self:
        needs_reason = self.target_stage in {Stage.REWORK, Stage.BLOCKED, Stage.FAILED}
        if needs_reason != (self.reason is not None):
            raise ValueError("reason is required only for rework, blocked, or failed transitions")
        expected_rework = 1 if self.target_stage is Stage.REWORK else 0
        if self.charge.rework_attempts != expected_rework:
            raise ValueError("rework transition must consume exactly one rework attempt")
        return self


def _require_artifact[ArtifactT: ArtifactBase](
    command: TransitionCommand, artifact_type: type[ArtifactT]
) -> ArtifactT:
    artifact = command.artifact
    if not isinstance(artifact, artifact_type):
        raise ArtifactGateError(f"{command.target_stage.value} requires {artifact_type.__name__}")
    return artifact


def _require_no_artifact(command: TransitionCommand) -> None:
    if command.artifact is not None:
        raise ArtifactGateError(f"{command.target_stage.value} does not accept an artifact")


def _validate_artifact_gate(state: WorkflowState, command: TransitionCommand) -> None:
    artifact = command.artifact
    if artifact is not None:
        if artifact.task_id != state.task_id or artifact.task_id != command.task_id:
            raise ArtifactGateError("artifact task does not match workflow task")
        if artifact.producer_id != command.actor_id:
            raise ArtifactGateError("transition actor must match artifact producer")
        if artifact.artifact_id in state.artifact_ids:
            raise ArtifactGateError("artifact has already been accepted")
        if artifact.created_at > command.occurred_at:
            raise ArtifactGateError("artifact cannot be accepted before its creation time")

    target = command.target_stage
    if target in {
        Stage.SPECIFYING,
        Stage.ANALYZING,
        Stage.IMPLEMENTING,
        Stage.VALIDATING,
        Stage.QA,
        Stage.REVIEW,
    }:
        _require_no_artifact(command)
    elif target is Stage.SPEC_READY:
        specification = _require_artifact(command, TaskSpecification)
        if specification.decision is not SpecificationDecision.READY:
            raise ArtifactGateError("spec_ready requires a ready specification")
    elif target is Stage.ANALYSIS_READY:
        _require_artifact(command, AnalysisReport)
    elif target is Stage.IMPLEMENTED:
        implementation = _require_artifact(command, ImplementationResult)
        if implementation.status is not ImplementationStatus.COMPLETED:
            raise ArtifactGateError("implemented requires a completed implementation")
    elif target is Stage.VALIDATED:
        validation = _require_artifact(command, ValidationResult)
        if validation.decision is not ValidationDecision.PASS:
            raise ArtifactGateError("validated requires passing deterministic validation")
    elif target is Stage.QA_PASSED:
        qa_report = _require_artifact(command, QAReport)
        if qa_report.decision is not QADecision.PASS:
            raise ArtifactGateError("qa_passed requires a passing QA report")
        if qa_report.implementation_author_id != state.implementation_author_id:
            raise ArtifactGateError("QA report references the wrong implementation author")
    elif target is Stage.DONE:
        review = _require_artifact(command, ReviewReport)
        if review.decision is not ReviewDecision.APPROVE:
            raise ArtifactGateError("done requires reviewer approval")
        if review.implementation_author_id != state.implementation_author_id:
            raise ArtifactGateError("review references the wrong implementation author")
    elif target is Stage.REWORK:
        if state.stage is Stage.VALIDATING:
            validation = _require_artifact(command, ValidationResult)
            if validation.decision is not ValidationDecision.FAIL:
                raise ArtifactGateError("validation rework requires a failed validation")
        elif state.stage is Stage.QA:
            qa_report = _require_artifact(command, QAReport)
            if qa_report.decision is not QADecision.FAIL:
                raise ArtifactGateError("QA rework requires a failing QA report")
            if qa_report.implementation_author_id != state.implementation_author_id:
                raise ArtifactGateError("QA report references the wrong implementation author")
        elif state.stage is Stage.REVIEW:
            review = _require_artifact(command, ReviewReport)
            if review.decision is not ReviewDecision.REQUEST_CHANGES:
                raise ArtifactGateError("review rework requires request_changes")
            if review.implementation_author_id != state.implementation_author_id:
                raise ArtifactGateError("review references the wrong implementation author")
    elif target is Stage.BLOCKED:
        if state.stage is Stage.SPECIFYING:
            specification = _require_artifact(command, TaskSpecification)
            valid = specification.decision is SpecificationDecision.BLOCKED
        elif state.stage is Stage.IMPLEMENTING:
            implementation = _require_artifact(command, ImplementationResult)
            valid = implementation.status is ImplementationStatus.BLOCKED
        elif state.stage is Stage.QA:
            qa_report = _require_artifact(command, QAReport)
            valid = qa_report.decision is QADecision.BLOCKED
            if qa_report.implementation_author_id != state.implementation_author_id:
                raise ArtifactGateError("QA report references the wrong implementation author")
        elif state.stage is Stage.REVIEW:
            review = _require_artifact(command, ReviewReport)
            valid = review.decision is ReviewDecision.BLOCKED
            if review.implementation_author_id != state.implementation_author_id:
                raise ArtifactGateError("review references the wrong implementation author")
        else:  # pragma: no cover - transition table rejects this first
            valid = False
        if not valid:
            raise ArtifactGateError("blocked transition requires a matching blocked artifact")
    elif target is Stage.FAILED:
        if state.stage is Stage.IMPLEMENTING:
            implementation = _require_artifact(command, ImplementationResult)
            valid = implementation.status is ImplementationStatus.FAILED
        elif state.stage is Stage.VALIDATING:
            validation = _require_artifact(command, ValidationResult)
            valid = validation.decision is ValidationDecision.ERROR
        else:  # pragma: no cover - transition table rejects this first
            valid = False
        if not valid:
            raise ArtifactGateError("failed transition requires a matching failure artifact")


def _charge_rework_or_fail(
    state: WorkflowState, command: TransitionCommand
) -> tuple[BudgetState, Stage, str | None]:
    remaining = state.budgets.remaining.rework_attempts
    normal_charge = BudgetCharge(
        tool_calls=command.charge.tool_calls,
        model_tokens=command.charge.model_tokens,
        wall_time_seconds=command.charge.wall_time_seconds,
        rework_attempts=0,
    )
    budgets = state.budgets.charge(normal_charge)
    if remaining == 0:
        return budgets, Stage.FAILED, f"rework budget exhausted: {command.reason}"
    return budgets.charge(BudgetCharge(rework_attempts=1)), Stage.REWORK, None


def apply_transition(state: WorkflowState, command: TransitionCommand) -> WorkflowState:
    """Validate one edge and return a new state without mutating its input."""

    if state.stage.terminal:
        raise IllegalTransitionError(f"terminal stage {state.stage.value} has no outgoing edges")
    if command.task_id != state.task_id:
        raise ArtifactGateError("transition task does not match workflow task")
    if command.target_stage not in ALLOWED_TRANSITIONS[state.stage]:
        raise IllegalTransitionError(
            f"transition {state.stage.value} -> {command.target_stage.value} is not allowed"
        )
    _validate_artifact_gate(state, command)

    if command.target_stage is Stage.REWORK:
        budgets, target_stage, terminal_reason = _charge_rework_or_fail(state, command)
    else:
        budgets = state.budgets.charge(command.charge)
        target_stage = command.target_stage
        terminal_reason = command.reason if target_stage in {Stage.BLOCKED, Stage.FAILED} else None

    artifact_ids = state.artifact_ids
    implementation_author = state.implementation_author_id
    if command.artifact is not None:
        artifact_ids = (*artifact_ids, command.artifact.artifact_id)
        if target_stage is Stage.IMPLEMENTED:
            implementation_author = command.artifact.producer_id

    return WorkflowState(
        workflow_id=state.workflow_id,
        correlation_id=state.correlation_id,
        task_id=state.task_id,
        stage=target_stage,
        revision=state.revision + 1,
        budgets=budgets,
        artifact_ids=artifact_ids,
        implementation_author_id=implementation_author,
        terminal_reason=terminal_reason,
    )
