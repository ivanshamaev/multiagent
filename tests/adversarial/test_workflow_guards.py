import ast
from pathlib import Path

import pytest
from pydantic import ValidationError

from contracts import (
    CheckResult,
    CheckStatus,
    CriterionAssessment,
    CriterionStatus,
    QADecision,
    QAReport,
    ReviewDecision,
    ReviewReport,
)
from orchestrator import ArtifactGateError, Stage, TransitionCommand, apply_transition
from tests.workflow.factories import TASK_ID, at, evidence, review_report
from tests.workflow.test_state_machine import _state_at

ROOT = Path(__file__).resolve().parents[2]


def test_qa_failure_cannot_omit_defect_or_evidence_link() -> None:
    item = evidence("qa-failure-evidence", 9, exit_code=1)
    payload = {
        "artifact_id": "qa-failure",
        "task_id": TASK_ID,
        "producer_id": "qa",
        "created_at": at(10),
        "implementation_author_id": "data-engineer",
        "decision": QADecision.FAIL,
        "checks": (
            CheckResult(
                check_id="failed-check",
                name="Failed check",
                status=CheckStatus.FAIL,
                evidence_ids=(item.evidence_id,),
            ),
        ),
        "defects": (),
        "summary": "Failure without defect.",
        "evidence": (item,),
    }
    with pytest.raises(ValidationError, match="requires a failed check and a defect"):
        QAReport.model_validate(payload)

    payload["defects"] = ()
    payload["checks"] = (
        CheckResult(
            check_id="failed-check",
            name="Failed check",
            status=CheckStatus.FAIL,
            evidence_ids=("invented-evidence",),
        ),
    )
    with pytest.raises(ValidationError, match="attached evidence"):
        QAReport.model_validate(payload)


def test_implementation_author_cannot_review_or_approve_self() -> None:
    payload = review_report().model_dump()
    payload["producer_id"] = payload["implementation_author_id"]

    with pytest.raises(ValidationError, match="own work"):
        ReviewReport.model_validate(payload)


def test_approval_cannot_hide_failed_criterion() -> None:
    item = evidence("review-evidence", 11)
    payload = {
        "artifact_id": "forged-approval",
        "task_id": TASK_ID,
        "producer_id": "reviewer",
        "created_at": at(12),
        "implementation_author_id": "data-engineer",
        "decision": ReviewDecision.APPROVE,
        "acceptance_criteria": (
            CriterionAssessment(
                criterion_id="criterion-failed",
                status=CriterionStatus.FAIL,
                rationale="It failed.",
                evidence_ids=(item.evidence_id,),
            ),
        ),
        "summary": "Approve anyway.",
        "evidence": (item,),
    }

    with pytest.raises(ValidationError, match="all criteria pass"):
        ReviewReport.model_validate(payload)


def test_reducer_checks_current_implementation_author() -> None:
    state = _state_at(Stage.REVIEW).model_copy(
        update={"implementation_author_id": "different-engineer"}
    )
    report = review_report()
    command = TransitionCommand(
        command_id="forged-review-transition",
        task_id=TASK_ID,
        actor_id="reviewer",
        target_stage=Stage.DONE,
        occurred_at=at(12),
        artifact=report,
    )

    with pytest.raises(ArtifactGateError, match="wrong implementation author"):
        apply_transition(state, command)


def test_production_code_never_uses_unvalidated_model_construct() -> None:
    offenders: list[str] = []
    for root_name in ("contracts", "orchestrator", "runtime"):
        for path in (ROOT / root_name).rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            if any(
                isinstance(node, ast.Attribute) and node.attr == "model_construct"
                for node in ast.walk(tree)
            ):
                offenders.append(path.relative_to(ROOT).as_posix())

    assert offenders == []
