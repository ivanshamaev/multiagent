from pathlib import Path

import pytest
from pydantic import ValidationError

from contracts import ToolName, ToolRequest
from policies import (
    CapabilityProfile,
    PolicyCode,
    ToolUsage,
    authorize_tool_call,
    load_capability_profile,
)

ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = ROOT / "policies/profiles/data_engineer_v1.json"


@pytest.fixture
def profile() -> CapabilityProfile:
    return load_capability_profile(PROFILE_PATH)


def _request(call: dict[str, object], *, role: str = "data-engineer") -> ToolRequest:
    return ToolRequest(
        request_id="request-1",
        task_id="task-1",
        actor_id="data-engineer-1",
        role=role,
        call=call,  # type: ignore[arg-type]
    )


@pytest.mark.parametrize(
    "call",
    [
        {"tool": "workspace.read_file", "path": "TASK.md"},
        {
            "tool": "workspace.write_file",
            "path": "platform/dbt/models/marts/fct_example.sql",
            "content": "select 1\n",
        },
        {"tool": "clickhouse.list_databases"},
        {"tool": "clickhouse.list_tables", "database": "raw"},
        {"tool": "clickhouse.run_query", "query": "SELECT * FROM raw.orders LIMIT 10"},
        {
            "tool": "clickhouse.run_query",
            "query": ("WITH source AS (SELECT * FROM raw.orders) SELECT * FROM source LIMIT 10"),
        },
        {"tool": "dbt.parse"},
        {"tool": "dbt.compile", "node_selection": "tag:hourly models.marts+"},
        {"tool": "dbt.build", "node_selection": "fct_net_revenue+"},
        {"tool": "dbt.test", "yml_selector": "hourly_validation"},
        {
            "tool": "dbt.show",
            "sql_query": "SELECT * FROM analytics.fct_net_revenue LIMIT 5",
            "limit": 5,
        },
        {"tool": "dbt.list", "resource_type": "model"},
        {"tool": "dbt.get_lineage_dev", "unique_id": "model.ecommerce.fct_net_revenue"},
        {"tool": "dbt.get_node_details_dev", "node_id": "model.ecommerce.fct_net_revenue"},
    ],
)
def test_data_engineer_profile_allows_only_bounded_calls(
    profile: CapabilityProfile,
    call: dict[str, object],
) -> None:
    decision = authorize_tool_call(profile, _request(call), ToolUsage())

    assert decision.allowed
    assert decision.code is PolicyCode.ALLOWED


def test_role_and_exact_tool_allowlist_are_enforced(profile: CapabilityProfile) -> None:
    wrong_role = authorize_tool_call(
        profile,
        _request({"tool": "dbt.parse"}, role="reviewer"),
        ToolUsage(),
    )
    narrowed_payload = profile.model_dump()
    narrowed_payload["allowed_tools"] = [ToolName.WORKSPACE_READ_FILE]
    narrowed = CapabilityProfile.model_validate(narrowed_payload)
    wrong_tool = authorize_tool_call(
        narrowed,
        _request({"tool": "clickhouse.list_databases"}),
        ToolUsage(),
    )

    assert wrong_role.code is PolicyCode.ROLE_DENIED
    assert wrong_tool.code is PolicyCode.TOOL_DENIED


@pytest.mark.parametrize(
    ("call", "code"),
    [
        ({"tool": "workspace.read_file", "path": ".env"}, PolicyCode.PATH_DENIED),
        ({"tool": "workspace.read_file", "path": "grader/oracle.py"}, PolicyCode.PATH_DENIED),
        (
            {
                "tool": "workspace.write_file",
                "path": "platform/airflow/dags/ecommerce_hourly.py",
                "content": "tamper",
            },
            PolicyCode.PATH_DENIED,
        ),
        (
            {"tool": "clickhouse.list_tables", "database": "system"},
            PolicyCode.DATABASE_DENIED,
        ),
    ],
)
def test_path_and_database_scope_are_denied(
    profile: CapabilityProfile,
    call: dict[str, object],
    code: PolicyCode,
) -> None:
    decision = authorize_tool_call(profile, _request(call), ToolUsage())

    assert not decision.allowed
    assert decision.code is code


@pytest.mark.parametrize(
    "query",
    [
        "INSERT INTO analytics.x VALUES (1)",
        "DROP TABLE analytics.x",
        "SELECT * FROM raw.orders LIMIT 1; SELECT 2 LIMIT 1",
        "SELECT * FROM system.tables LIMIT 10",
        "SELECT * FROM orders LIMIT 10",
        "SELECT * FROM file('/etc/passwd') LIMIT 10",
        "SELECT dictGet('secret', 'value', 1) LIMIT 1",
        "SELECT * FROM raw.orders",
        "SELECT * FROM raw.orders LIMIT 101",
        "SELECT * FROM raw.orders LIMIT 1 + 1",
        "SELECT * FROM raw.orders LIMIT 1 SETTINGS max_execution_time=100",
        "EXPLAIN SELECT * FROM raw.orders LIMIT 1",
    ],
)
def test_sql_ast_gate_rejects_unsafe_or_unbounded_queries(
    profile: CapabilityProfile,
    query: str,
) -> None:
    decision = authorize_tool_call(
        profile,
        _request({"tool": "clickhouse.run_query", "query": query}),
        ToolUsage(),
    )

    assert not decision.allowed
    assert decision.code is PolicyCode.QUERY_DENIED


@pytest.mark.parametrize(
    "usage",
    [
        ToolUsage(completed_calls=80),
        ToolUsage(elapsed_ms=1_200_000),
        ToolUsage(output_bytes=2_000_000),
    ],
)
def test_exhausted_budget_denies_before_call(
    profile: CapabilityProfile,
    usage: ToolUsage,
) -> None:
    decision = authorize_tool_call(profile, _request({"tool": "dbt.parse"}), usage)

    assert not decision.allowed
    assert decision.code is PolicyCode.BUDGET_DENIED


def test_profile_is_closed_versioned_and_has_unique_allowlists(profile: CapabilityProfile) -> None:
    assert profile.schema_version == 1
    payload = profile.model_dump(mode="json")

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        CapabilityProfile.model_validate({**payload, "allow_shell": True})
    with pytest.raises(ValidationError, match="duplicates"):
        CapabilityProfile.model_validate(
            {**payload, "allowed_tools": [*payload["allowed_tools"], "dbt.parse"]}
        )
    with pytest.raises(ValidationError, match="path pattern"):
        CapabilityProfile.model_validate({**payload, "writable_paths": ["../**"]})
