from pathlib import Path

import pytest

from contracts import ToolRequest
from policies import PolicyCode, ToolUsage, authorize_tool_call, load_capability_profile

ROOT = Path(__file__).resolve().parents[2]
PROFILE = load_capability_profile(ROOT / "policies/profiles/qa_v1.json")


def _request(call: dict[str, object], *, role: str = "qa") -> ToolRequest:
    return ToolRequest(
        request_id="qa-request-1",
        task_id="scenario-net-revenue",
        actor_id="qa-agent",
        role=role,
        call=call,  # type: ignore[arg-type]
    )


@pytest.mark.parametrize(
    "call",
    [
        {
            "tool": "workspace.read_file",
            "path": "platform/dbt/models/marts/fct_net_revenue.sql",
        },
        {
            "tool": "clickhouse.run_query",
            "query": "SELECT count() FROM analytics.fct_net_revenue LIMIT 1",
        },
        {
            "tool": "dbt.show",
            "sql_query": "SELECT * FROM analytics.fct_net_revenue",
            "limit": 5,
        },
        {"tool": "dbt.list", "node_selection": "fct_net_revenue"},
    ],
)
def test_qa_profile_allows_only_bounded_read_operations(call: dict[str, object]) -> None:
    decision = authorize_tool_call(PROFILE, _request(call), ToolUsage())

    assert decision.allowed


@pytest.mark.parametrize(
    "call",
    [
        {
            "tool": "workspace.write_file",
            "path": "platform/dbt/models/marts/fct_net_revenue.sql",
            "content": "select 1\n",
        },
        {"tool": "dbt.build", "node_selection": "fct_net_revenue"},
        {"tool": "dbt.test", "node_selection": "fct_net_revenue"},
        {"tool": "workspace.read_file", "path": "grader/hidden/grade.py"},
        {"tool": "clickhouse.run_query", "query": "DROP TABLE analytics.fct_net_revenue"},
    ],
)
def test_qa_profile_denies_write_execution_grader_and_ddl(call: dict[str, object]) -> None:
    decision = authorize_tool_call(PROFILE, _request(call), ToolUsage())

    assert not decision.allowed


def test_qa_identity_cannot_reuse_data_engineer_role() -> None:
    decision = authorize_tool_call(
        PROFILE,
        _request({"tool": "dbt.list"}, role="data-engineer"),
        ToolUsage(),
    )

    assert decision.code is PolicyCode.ROLE_DENIED
