from pathlib import Path

import pytest

from contracts import (
    ClickHouseRunQueryCall,
    DbtBuildCall,
    ToolRequest,
    WorkspaceReadCall,
    WorkspaceWriteCall,
)
from policies import PolicyCode, ToolUsage, authorize_tool_call, load_capability_profile
from runtime.analyst import ANALYST_PROFILE_SQL

ROOT = Path(__file__).resolve().parents[2]
PROFILE = load_capability_profile(ROOT / "policies/profiles/analyst_v1.json")


def _decision(call, *, role="analyst"):
    return authorize_tool_call(
        PROFILE,
        ToolRequest(
            request_id="request-1",
            task_id="task-1",
            actor_id="analyst-agent",
            role=role,
            call=call,
        ),
        ToolUsage(),
    )


def test_analyst_allows_bounded_select_and_model_metadata_reads() -> None:
    assert _decision(WorkspaceReadCall(path="platform/dbt/models/marts/fct_orders.sql")).allowed
    assert _decision(ClickHouseRunQueryCall(query="SELECT count() FROM raw.orders LIMIT 1")).allowed
    assert "ordered_at" in ANALYST_PROFILE_SQL
    assert "order_date" not in ANALYST_PROFILE_SQL


@pytest.mark.parametrize(
    "call",
    [
        WorkspaceWriteCall(path="platform/dbt/models/marts/new.sql", content="select 1"),
        DbtBuildCall(),
        WorkspaceReadCall(path=".env"),
        ClickHouseRunQueryCall(query="SELECT * FROM raw.orders"),
        ClickHouseRunQueryCall(query="DROP TABLE raw.orders"),
        ClickHouseRunQueryCall(query="SELECT * FROM system.tables LIMIT 1"),
    ],
)
def test_analyst_denies_writes_builds_secrets_and_unsafe_sql(call) -> None:
    assert not _decision(call).allowed


def test_wrong_role_is_denied_before_tool_use() -> None:
    decision = _decision(WorkspaceReadCall(path="TASK.md"), role="data-engineer")
    assert decision.code is PolicyCode.ROLE_DENIED
