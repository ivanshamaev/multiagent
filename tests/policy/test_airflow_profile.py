from pathlib import Path

import pytest
from pydantic import ValidationError

from contracts import ToolRequest
from policies import PolicyCode, ToolUsage, authorize_tool_call, load_capability_profile

ROOT = Path(__file__).resolve().parents[2]
PROFILE = load_capability_profile(ROOT / "policies/profiles/airflow_observer_v1.json")


def _request(call: dict[str, object], *, role: str = "airflow-observer") -> ToolRequest:
    return ToolRequest(
        request_id="request-airflow",
        task_id="task-airflow",
        actor_id="airflow-observer-agent",
        role=role,
        call=call,  # type: ignore[arg-type]
    )


@pytest.mark.parametrize(
    "call",
    [
        {"tool": "airflow.list_dags"},
        {"tool": "airflow.get_dag", "dag_id": "ecommerce_hourly"},
        {"tool": "airflow.list_dag_runs", "dag_id": "ecommerce_acceptance", "limit": 5},
        {
            "tool": "airflow.get_dag_run",
            "dag_id": "ecommerce_acceptance",
            "dag_run_id": "manual__one",
        },
        {
            "tool": "airflow.list_task_instances",
            "dag_id": "ecommerce_acceptance",
            "dag_run_id": "manual__one",
        },
        {
            "tool": "airflow.get_task_log",
            "dag_id": "ecommerce_acceptance",
            "dag_run_id": "manual__one",
            "task_id": "publish",
            "try_number": 1,
        },
    ],
)
def test_observer_profile_allows_only_bounded_read_calls(call: dict[str, object]) -> None:
    assert authorize_tool_call(PROFILE, _request(call), ToolUsage()).allowed


def test_observer_profile_denies_wrong_role_dag_tool_and_budget() -> None:
    wrong_role = authorize_tool_call(
        PROFILE,
        _request({"tool": "airflow.list_dags"}, role="data-engineer"),
        ToolUsage(),
    )
    wrong_dag = authorize_tool_call(
        PROFILE,
        _request({"tool": "airflow.get_dag", "dag_id": "secret_pipeline"}),
        ToolUsage(),
    )
    wrong_tool = authorize_tool_call(
        PROFILE,
        _request({"tool": "dbt.parse"}),
        ToolUsage(),
    )
    exhausted = authorize_tool_call(
        PROFILE,
        _request({"tool": "airflow.list_dags"}),
        ToolUsage(completed_calls=PROFILE.max_tool_calls),
    )

    assert wrong_role.code is PolicyCode.ROLE_DENIED
    assert wrong_dag.code is PolicyCode.AIRFLOW_DAG_DENIED
    assert wrong_tool.code is PolicyCode.TOOL_DENIED
    assert exhausted.code is PolicyCode.BUDGET_DENIED


@pytest.mark.parametrize(
    "call",
    [
        {"tool": "airflow.get_dag", "dag_id": "../../admin"},
        {"tool": "airflow.list_dag_runs", "dag_id": "dag?limit=1000"},
        {
            "tool": "airflow.get_task_log",
            "dag_id": "ecommerce_acceptance",
            "dag_run_id": "manual__one",
            "task_id": "publish",
            "try_number": 0,
        },
        {"tool": "airflow.trigger_dag", "dag_id": "ecommerce_acceptance"},
        {"tool": "airflow.patch_dag", "dag_id": "ecommerce_acceptance"},
    ],
)
def test_write_unknown_and_unbounded_shapes_have_no_contract(call: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        _request(call)
