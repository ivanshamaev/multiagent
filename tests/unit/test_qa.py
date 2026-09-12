from pathlib import Path

import pytest
from pydantic import ValidationError

from contracts import ClickHouseRunQueryCall, ToolRequest
from policies import ToolUsage, authorize_tool_call, load_capability_profile
from runtime.qa import QA_READ_ONLY_TOOLS, QA_SEMANTIC_PROBE_SQL, QADraft, qa_system_prompt

ROOT = Path(__file__).resolve().parents[2]


def test_qa_draft_requires_complete_defect_only_for_failure() -> None:
    passing = QADraft(
        decision="pass",
        check_name="semantic counterexample probe",
        summary="No counterexample was returned.",
    )
    failing = QADraft(
        decision="fail",
        check_name="late refund attribution",
        summary="Late refund moved to its event date.",
        defect_description="Refund is not attributed to the original order date.",
        acceptance_criterion="refunds inherit the original order date",
        severity="high",
    )

    assert passing.defect_description is None
    assert failing.severity.value == "high"
    with pytest.raises(ValidationError, match="complete defect"):
        QADraft(
            decision="fail",
            check_name="refund check",
            summary="A counterexample exists.",
        )
    with pytest.raises(ValidationError, match="only failing"):
        QADraft(
            decision="pass",
            check_name="refund check",
            summary="No counterexample exists.",
            defect_description="invented",
        )


def test_qa_instructions_and_code_allowlist_are_read_only() -> None:
    instructions = qa_system_prompt()

    assert "independently test" in instructions
    assert "Never claim or request write" in instructions
    assert all("write" not in item.value for item in QA_READ_ONLY_TOOLS)
    assert (ROOT / "agents/qa/instructions.md").is_file()


def test_public_semantic_probe_is_accepted_by_the_qa_sql_policy() -> None:
    profile = load_capability_profile(ROOT / "policies/profiles/qa_v1.json")
    request = ToolRequest(
        request_id="qa-public-probe",
        task_id="scenario-net-revenue",
        actor_id="qa-agent",
        role="qa",
        call=ClickHouseRunQueryCall(query=QA_SEMANTIC_PROBE_SQL),
    )

    assert authorize_tool_call(profile, request, ToolUsage()).allowed
