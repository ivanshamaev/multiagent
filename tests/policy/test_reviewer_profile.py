from pathlib import Path

import pytest

from contracts import ToolRequest
from policies import PolicyCode, ToolUsage, authorize_tool_call, load_capability_profile

ROOT = Path(__file__).resolve().parents[2]
PROFILE = load_capability_profile(ROOT / "policies/profiles/reviewer_v1.json")


def _request(call: dict[str, object], *, role: str = "reviewer") -> ToolRequest:
    return ToolRequest(
        request_id="reviewer-request-1",
        task_id="scenario-net-revenue",
        actor_id="reviewer-agent",
        role=role,
        call=call,  # type: ignore[arg-type]
    )


@pytest.mark.parametrize(
    "path",
    [
        "platform/dbt/models/marts/fct_net_revenue.sql",
        "platform/dbt/tests/assert_fct_net_revenue_contract.sql",
    ],
)
def test_reviewer_profile_allows_only_candidate_reads(path: str) -> None:
    decision = authorize_tool_call(
        PROFILE,
        _request({"tool": "workspace.read_file", "path": path}),
        ToolUsage(),
    )
    assert decision.allowed


@pytest.mark.parametrize(
    "call",
    [
        {"tool": "workspace.read_file", "path": "grader/hidden/grade.py"},
        {"tool": "workspace.read_file", "path": "TASK.md"},
        {
            "tool": "workspace.write_file",
            "path": "platform/dbt/models/marts/fct_net_revenue.sql",
            "content": "select 1\n",
        },
        {"tool": "dbt.parse"},
        {"tool": "dbt.test", "node_selection": "fct_net_revenue"},
        {"tool": "clickhouse.run_query", "query": "SELECT 1 LIMIT 1"},
    ],
)
def test_reviewer_profile_denies_extra_reads_write_and_execution(
    call: dict[str, object],
) -> None:
    assert not authorize_tool_call(PROFILE, _request(call), ToolUsage()).allowed


def test_reviewer_profile_rejects_wrong_role() -> None:
    decision = authorize_tool_call(
        PROFILE,
        _request(
            {
                "tool": "workspace.read_file",
                "path": "platform/dbt/models/marts/fct_net_revenue.sql",
            },
            role="qa",
        ),
        ToolUsage(),
    )
    assert decision.code is PolicyCode.ROLE_DENIED
