from pathlib import Path

import pytest
from pydantic import ValidationError

from runtime.reviewer import (
    REVIEWER_READ_ONLY_TOOLS,
    ReviewerCriterionDraft,
    ReviewerDraft,
    reviewer_system_prompt,
)

ROOT = Path(__file__).resolve().parents[2]


def _criterion(status: str = "pass") -> ReviewerCriterionDraft:
    return ReviewerCriterionDraft(
        criterion="the immutable criterion",
        status=status,
        rationale="The candidate and test provide direct evidence.",
    )


def test_reviewer_draft_enforces_decision_shape() -> None:
    approved = ReviewerDraft(
        decision="approve",
        acceptance_criteria=(_criterion(),),
        summary="All criteria are covered.",
    )
    assert approved.decision.value == "approve"

    with pytest.raises(ValidationError, match="all criteria pass"):
        ReviewerDraft(
            decision="approve",
            acceptance_criteria=(_criterion("fail"),),
            summary="Contradictory approval.",
        )
    with pytest.raises(ValidationError, match="failed criterion or finding"):
        ReviewerDraft(
            decision="request_changes",
            acceptance_criteria=(_criterion(),),
            summary="No actionable defect.",
        )


def test_reviewer_instructions_and_allowlist_are_read_only() -> None:
    instructions = reviewer_system_prompt()
    assert "independently decide" in instructions
    assert "Never request write" in instructions
    assert REVIEWER_READ_ONLY_TOOLS == {"workspace.read_file"}
    assert (ROOT / "agents/reviewer/instructions.md").is_file()
