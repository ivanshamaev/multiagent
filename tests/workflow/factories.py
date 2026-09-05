"""Valid version-one contract factories used by workflow tests."""

from datetime import UTC, datetime, timedelta

from contracts import (
    AnalysisReport,
    ArtifactReference,
    CheckResult,
    CheckStatus,
    CriterionAssessment,
    CriterionStatus,
    Evidence,
    EvidenceKind,
    ImplementationResult,
    ImplementationStatus,
    QADecision,
    QAReport,
    ReviewDecision,
    ReviewReport,
    SpecificationDecision,
    TaskRequest,
    TaskSpecification,
    ValidationDecision,
    ValidationResult,
)
from orchestrator import BudgetLimits

TASK_ID = "TASK-001"
BASE_TIME = datetime(2026, 9, 5, 18, 0, tzinfo=UTC)


def at(second: int) -> datetime:
    return BASE_TIME + timedelta(seconds=second)


def evidence(
    evidence_id: str,
    second: int,
    *,
    exit_code: int = 0,
    task_id: str = TASK_ID,
    producer_id: str = "validator",
) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        task_id=task_id,
        producer_id=producer_id,
        kind=EvidenceKind.TEST,
        source="pytest",
        invocation=f"pytest -k {evidence_id}",
        exit_code=exit_code,
        artifact=ArtifactReference(
            path=f"artifacts/{task_id}/{evidence_id}.json",
            sha256="a" * 64,
            media_type="application/json",
            size_bytes=128,
        ),
        occurred_at=at(second),
    )


def task_request(*, task_id: str = TASK_ID) -> TaskRequest:
    return TaskRequest(
        artifact_id="artifact-task-request",
        task_id=task_id,
        producer_id="user",
        created_at=at(0),
        title="Add Net Revenue",
        description="Create a verified Net Revenue mart.",
    )


def specification(
    *,
    decision: SpecificationDecision = SpecificationDecision.READY,
    task_id: str = TASK_ID,
) -> TaskSpecification:
    blocked = decision is SpecificationDecision.BLOCKED
    return TaskSpecification(
        artifact_id=f"artifact-spec-{decision.value}",
        task_id=task_id,
        producer_id="pm",
        created_at=at(2),
        decision=decision,
        business_goal="Expose Net Revenue for reporting.",
        metric_definition=None if blocked else "payments minus refunds",
        grain=() if blocked else ("order_date", "country", "channel", "currency"),
        dimensions=() if blocked else ("country", "channel", "currency"),
        source_requirements=() if blocked else ("orders", "payments", "refunds"),
        acceptance_criteria=() if blocked else ("metric identity holds",),
        open_questions=("Which currency policy applies?",) if blocked else (),
    )


def analysis_report() -> AnalysisReport:
    item = evidence("evidence-analysis", 3, producer_id="analyst-tool")
    return AnalysisReport(
        artifact_id="artifact-analysis",
        task_id=TASK_ID,
        producer_id="analyst",
        created_at=at(4),
        relevant_sources=("raw.orders", "raw.payments", "raw.refunds"),
        relevant_models=("analytics.fct_orders",),
        lineage=("raw.orders -> analytics.fct_orders",),
        findings=("Refunds can arrive after the order date.",),
        recommended_approach="Aggregate events per order before the reporting grain.",
        semantic_risks=("Currencies have no conversion table.",),
        evidence=(item,),
    )


def implementation_result(
    *,
    artifact_id: str = "artifact-implementation-1",
    producer_id: str = "data-engineer",
    status: ImplementationStatus = ImplementationStatus.COMPLETED,
) -> ImplementationResult:
    item = evidence(f"evidence-{artifact_id}", 5, producer_id="dbt")
    return ImplementationResult(
        artifact_id=artifact_id,
        task_id=TASK_ID,
        producer_id=producer_id,
        created_at=at(6),
        status=status,
        changed_files=("platform/dbt/models/marts/fct_net_revenue.sql",)
        if status is ImplementationStatus.COMPLETED
        else (),
        summary=(
            "Implemented candidate." if status is ImplementationStatus.COMPLETED else "Stopped."
        ),
        tests_executed=(item.evidence_id,),
        known_issues=() if status is ImplementationStatus.COMPLETED else ("Tool failed.",),
        evidence=(item,),
    )


def validation_result(
    *,
    decision: ValidationDecision = ValidationDecision.PASS,
    artifact_id: str = "artifact-validation",
) -> ValidationResult:
    item = evidence(
        f"evidence-{artifact_id}",
        7,
        exit_code=0 if decision is ValidationDecision.PASS else 1,
    )
    return ValidationResult(
        artifact_id=artifact_id,
        task_id=TASK_ID,
        producer_id="validator",
        created_at=at(8),
        decision=decision,
        gates=("dbt build", "policy tests"),
        summary=f"Validation {decision.value}.",
        evidence=(item,),
    )


def qa_report(*, decision: QADecision = QADecision.PASS) -> QAReport:
    item = evidence(
        f"evidence-qa-{decision.value}",
        9,
        exit_code=1 if decision is QADecision.FAIL else 0,
        producer_id="qa-tool",
    )
    status = {
        QADecision.PASS: CheckStatus.PASS,
        QADecision.FAIL: CheckStatus.FAIL,
        QADecision.BLOCKED: CheckStatus.BLOCKED,
    }[decision]
    defects = ()
    if decision is QADecision.FAIL:
        from contracts import Defect, Severity

        defects = (
            Defect(
                defect_id="defect-net-revenue",
                severity=Severity.HIGH,
                description="Partial refunds are counted incorrectly.",
                acceptance_criterion="metric identity holds",
                evidence_ids=(item.evidence_id,),
            ),
        )
    return QAReport(
        artifact_id=f"artifact-qa-{decision.value}",
        task_id=TASK_ID,
        producer_id="qa",
        created_at=at(10),
        implementation_author_id="data-engineer",
        decision=decision,
        checks=(
            CheckResult(
                check_id="check-net-revenue",
                name="Net Revenue correctness",
                status=status,
                evidence_ids=(item.evidence_id,),
            ),
        ),
        defects=defects,
        summary=f"QA {decision.value}.",
        evidence=(item,),
    )


def review_report(*, decision: ReviewDecision = ReviewDecision.APPROVE) -> ReviewReport:
    item = evidence(
        f"evidence-review-{decision.value}",
        11,
        exit_code=1 if decision is ReviewDecision.REQUEST_CHANGES else 0,
        producer_id="review-tool",
    )
    criterion_status = {
        ReviewDecision.APPROVE: CriterionStatus.PASS,
        ReviewDecision.REQUEST_CHANGES: CriterionStatus.FAIL,
        ReviewDecision.BLOCKED: CriterionStatus.NOT_ASSESSED,
    }[decision]
    return ReviewReport(
        artifact_id=f"artifact-review-{decision.value}",
        task_id=TASK_ID,
        producer_id="reviewer",
        created_at=at(12),
        implementation_author_id="data-engineer",
        decision=decision,
        acceptance_criteria=(
            CriterionAssessment(
                criterion_id="criterion-metric",
                status=criterion_status,
                rationale="Compared independent outputs.",
                evidence_ids=(item.evidence_id,),
            ),
        ),
        summary=f"Review {decision.value}.",
        evidence=(item,),
    )


def budget_limits(*, rework_attempts: int = 2) -> BudgetLimits:
    return BudgetLimits(
        tool_calls=100,
        model_tokens=50_000,
        wall_time_seconds=3_600,
        rework_attempts=rework_attempts,
    )
