"""Version-one artifacts exchanged across deterministic workflow gates."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import Field, field_validator, model_validator

from contracts.common import (
    FrozenModel,
    Identifier,
    NonEmptyText,
    RelativePath,
    ShortText,
    UtcDateTime,
    VersionedModel,
    ensure_unique,
)
from contracts.evidence import EvidenceTuple, NonEmptyEvidenceTuple

TextTuple = Annotated[tuple[NonEmptyText, ...], Field(max_length=256)]
RequiredTextTuple = Annotated[tuple[NonEmptyText, ...], Field(min_length=1, max_length=256)]
RequiredIdentifierTuple = Annotated[tuple[Identifier, ...], Field(min_length=1, max_length=256)]


class SpecificationDecision(StrEnum):
    READY = "ready"
    BLOCKED = "blocked"


class ImplementationStatus(StrEnum):
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class ValidationDecision(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"


class CheckStatus(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    BLOCKED = "blocked"


class QADecision(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    BLOCKED = "blocked"


class ReviewDecision(StrEnum):
    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"
    BLOCKED = "blocked"


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CriterionStatus(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    NOT_ASSESSED = "not_assessed"


class ArtifactBase(VersionedModel):
    """Identity and authorship fields controlled at the workflow boundary."""

    artifact_id: Identifier
    task_id: Identifier
    producer_id: Identifier
    created_at: UtcDateTime
    evidence: EvidenceTuple = ()

    @model_validator(mode="after")
    def validate_evidence_scope(self) -> Self:
        evidence_ids = tuple(item.evidence_id for item in self.evidence)
        ensure_unique(evidence_ids, "evidence")
        if any(item.task_id != self.task_id for item in self.evidence):
            raise ValueError("all evidence must belong to the artifact task")
        if any(item.occurred_at > self.created_at for item in self.evidence):
            raise ValueError("evidence cannot occur after artifact creation")
        return self


class TaskRequest(ArtifactBase):
    artifact_type: Literal["task_request"] = "task_request"
    title: ShortText
    description: NonEmptyText


class TaskSpecification(ArtifactBase):
    artifact_type: Literal["task_specification"] = "task_specification"
    decision: SpecificationDecision
    business_goal: NonEmptyText
    metric_definition: NonEmptyText | None = None
    grain: TextTuple = ()
    dimensions: TextTuple = ()
    source_requirements: TextTuple = ()
    acceptance_criteria: TextTuple = ()
    non_functional_requirements: TextTuple = ()
    assumptions: TextTuple = ()
    open_questions: TextTuple = ()
    risks: TextTuple = ()

    @field_validator(
        "grain",
        "dimensions",
        "source_requirements",
        "acceptance_criteria",
        "non_functional_requirements",
        "assumptions",
        "open_questions",
        "risks",
    )
    @classmethod
    def unique_lists(cls, value: TextTuple, info) -> TextTuple:
        return ensure_unique(value, info.field_name)

    @model_validator(mode="after")
    def validate_decision(self) -> Self:
        if self.decision is SpecificationDecision.READY:
            if self.metric_definition is None:
                raise ValueError("ready specification requires metric_definition")
            if not self.grain or not self.dimensions or not self.source_requirements:
                raise ValueError("ready specification requires grain, dimensions, and sources")
            if not self.acceptance_criteria:
                raise ValueError("ready specification requires acceptance criteria")
            if self.open_questions:
                raise ValueError("ready specification cannot contain open questions")
        elif not self.open_questions:
            raise ValueError("blocked specification requires open questions")
        return self


class AnalysisReport(ArtifactBase):
    artifact_type: Literal["analysis_report"] = "analysis_report"
    relevant_sources: RequiredTextTuple
    relevant_models: TextTuple = ()
    lineage: TextTuple = ()
    findings: RequiredTextTuple
    recommended_approach: NonEmptyText
    semantic_risks: TextTuple = ()
    evidence: NonEmptyEvidenceTuple

    @field_validator("relevant_sources", "relevant_models", "lineage", "findings", "semantic_risks")
    @classmethod
    def unique_lists(cls, value: TextTuple, info) -> TextTuple:
        return ensure_unique(value, info.field_name)


class ImplementationResult(ArtifactBase):
    artifact_type: Literal["implementation_result"] = "implementation_result"
    status: ImplementationStatus
    changed_files: Annotated[tuple[RelativePath, ...], Field(max_length=256)] = ()
    summary: NonEmptyText
    tests_executed: Annotated[tuple[Identifier, ...], Field(max_length=256)] = ()
    known_issues: TextTuple = ()
    evidence: NonEmptyEvidenceTuple

    @field_validator("changed_files", "tests_executed", "known_issues")
    @classmethod
    def unique_lists(cls, value: tuple[str, ...], info) -> tuple[str, ...]:
        return ensure_unique(value, info.field_name)

    @model_validator(mode="after")
    def validate_status(self) -> Self:
        evidence_ids = {item.evidence_id for item in self.evidence}
        if not set(self.tests_executed).issubset(evidence_ids):
            raise ValueError("tests_executed must reference attached evidence")
        if self.status is ImplementationStatus.COMPLETED and not self.changed_files:
            raise ValueError("completed implementation requires changed_files")
        if self.status in {ImplementationStatus.BLOCKED, ImplementationStatus.FAILED}:
            if not self.known_issues:
                raise ValueError("blocked or failed implementation requires known_issues")
        return self


class ValidationResult(ArtifactBase):
    artifact_type: Literal["validation_result"] = "validation_result"
    decision: ValidationDecision
    gates: RequiredTextTuple
    summary: NonEmptyText
    evidence: NonEmptyEvidenceTuple

    @field_validator("gates")
    @classmethod
    def unique_gates(cls, value: TextTuple) -> TextTuple:
        return ensure_unique(value, "gates")

    @model_validator(mode="after")
    def validate_decision(self) -> Self:
        failures = [item for item in self.evidence if not item.succeeded]
        if self.decision is ValidationDecision.PASS and failures:
            raise ValueError("passing validation cannot contain failed evidence")
        if self.decision is not ValidationDecision.PASS and not failures:
            raise ValueError("failed validation requires non-zero evidence")
        return self


class CheckResult(FrozenModel):
    check_id: Identifier
    name: ShortText
    status: CheckStatus
    evidence_ids: RequiredIdentifierTuple

    @field_validator("evidence_ids")
    @classmethod
    def unique_evidence(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return ensure_unique(value, "evidence_ids")


class Defect(FrozenModel):
    defect_id: Identifier
    severity: Severity
    description: NonEmptyText
    acceptance_criterion: ShortText
    evidence_ids: RequiredIdentifierTuple

    @field_validator("evidence_ids")
    @classmethod
    def unique_evidence(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return ensure_unique(value, "evidence_ids")


class QAReport(ArtifactBase):
    artifact_type: Literal["qa_report"] = "qa_report"
    implementation_author_id: Identifier
    decision: QADecision
    checks: Annotated[tuple[CheckResult, ...], Field(min_length=1, max_length=256)]
    defects: tuple[Defect, ...] = ()
    summary: NonEmptyText
    evidence: NonEmptyEvidenceTuple

    @model_validator(mode="after")
    def validate_decision(self) -> Self:
        if self.producer_id == self.implementation_author_id:
            raise ValueError("implementation author cannot perform independent QA")
        evidence_ids = {item.evidence_id for item in self.evidence}
        references = {
            evidence_id
            for item in (*self.checks, *self.defects)
            for evidence_id in item.evidence_ids
        }
        if not references.issubset(evidence_ids):
            raise ValueError("QA checks and defects must reference attached evidence")
        statuses = {item.status for item in self.checks}
        if self.decision is QADecision.PASS:
            if statuses != {CheckStatus.PASS} or self.defects:
                raise ValueError("QA pass requires all checks pass and no defects")
            if any(not item.succeeded for item in self.evidence):
                raise ValueError("QA pass cannot contain failed evidence")
        elif self.decision is QADecision.FAIL:
            if CheckStatus.FAIL not in statuses or not self.defects:
                raise ValueError("QA fail requires a failed check and a defect")
        elif CheckStatus.BLOCKED not in statuses:
            raise ValueError("blocked QA requires a blocked check")
        return self


class ReviewFinding(FrozenModel):
    finding_id: Identifier
    severity: Severity
    description: NonEmptyText
    acceptance_criterion: ShortText
    evidence_ids: RequiredIdentifierTuple

    @field_validator("evidence_ids")
    @classmethod
    def unique_evidence(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return ensure_unique(value, "evidence_ids")


class CriterionAssessment(FrozenModel):
    criterion_id: Identifier
    status: CriterionStatus
    rationale: NonEmptyText
    evidence_ids: RequiredIdentifierTuple

    @field_validator("evidence_ids")
    @classmethod
    def unique_evidence(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return ensure_unique(value, "evidence_ids")


class ReviewReport(ArtifactBase):
    artifact_type: Literal["review_report"] = "review_report"
    implementation_author_id: Identifier
    decision: ReviewDecision
    findings: tuple[ReviewFinding, ...] = ()
    acceptance_criteria: Annotated[
        tuple[CriterionAssessment, ...], Field(min_length=1, max_length=256)
    ]
    risks: TextTuple = ()
    summary: NonEmptyText
    evidence: NonEmptyEvidenceTuple

    @model_validator(mode="after")
    def validate_decision(self) -> Self:
        if self.producer_id == self.implementation_author_id:
            raise ValueError("implementation author cannot approve or review own work")
        evidence_ids = {item.evidence_id for item in self.evidence}
        references = {
            evidence_id
            for item in (*self.findings, *self.acceptance_criteria)
            for evidence_id in item.evidence_ids
        }
        if not references.issubset(evidence_ids):
            raise ValueError("review findings and criteria must reference attached evidence")
        criteria = {item.status for item in self.acceptance_criteria}
        blocking_findings = {
            item.severity
            for item in self.findings
            if item.severity in {Severity.HIGH, Severity.CRITICAL}
        }
        if self.decision is ReviewDecision.APPROVE:
            if criteria != {CriterionStatus.PASS} or blocking_findings:
                raise ValueError("approval requires all criteria pass and no blocking findings")
            if any(not item.succeeded for item in self.evidence):
                raise ValueError("approval cannot contain failed evidence")
        elif self.decision is ReviewDecision.REQUEST_CHANGES:
            if CriterionStatus.FAIL not in criteria and not self.findings:
                raise ValueError("request_changes requires a failed criterion or finding")
        elif CriterionStatus.NOT_ASSESSED not in criteria:
            raise ValueError("blocked review requires a not_assessed criterion")
        return self


Artifact = Annotated[
    TaskRequest
    | TaskSpecification
    | AnalysisReport
    | ImplementationResult
    | ValidationResult
    | QAReport
    | ReviewReport,
    Field(discriminator="artifact_type"),
]
