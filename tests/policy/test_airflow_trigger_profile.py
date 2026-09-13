from pathlib import Path

from contracts import ToolRequest
from policies import PolicyCode, ToolUsage, authorize_tool_call, load_capability_profile

ROOT = Path(__file__).resolve().parents[2]
TRIGGER = load_capability_profile(ROOT / "policies/profiles/airflow_trigger_v1.json")
OBSERVER = load_capability_profile(ROOT / "policies/profiles/airflow_observer_v1.json")


def _request(
    *,
    task_id: str = "task-airflow-trigger",
    call_task_id: str = "task-airflow-trigger",
    dag_id: str = "ecommerce_acceptance",
    role: str = "airflow-trigger-controller",
) -> ToolRequest:
    return ToolRequest(
        request_id="request-airflow-trigger",
        task_id=task_id,
        actor_id="airflow-trigger-agent",
        role=role,
        call={
            "tool": "airflow.trigger_dag",
            "task_id": call_task_id,
            "dag_id": dag_id,
            "idempotency_key": "release-20260913",
            "approval_id": "airflow-approval-unit",
        },
    )


def test_trigger_profile_allows_exact_task_dag_and_role() -> None:
    assert authorize_tool_call(TRIGGER, _request(), ToolUsage()).allowed


def test_trigger_profile_denies_wrong_role_task_dag_and_budget() -> None:
    wrong_role = authorize_tool_call(
        TRIGGER,
        _request(role="airflow-observer"),
        ToolUsage(),
    )
    wrong_task = authorize_tool_call(
        TRIGGER,
        _request(call_task_id="other-task"),
        ToolUsage(),
    )
    wrong_dag = authorize_tool_call(
        TRIGGER,
        _request(dag_id="ecommerce_hourly"),
        ToolUsage(),
    )
    exhausted = authorize_tool_call(
        TRIGGER,
        _request(),
        ToolUsage(completed_calls=TRIGGER.max_tool_calls),
    )

    assert wrong_role.code is PolicyCode.ROLE_DENIED
    assert wrong_task.code is PolicyCode.REQUEST_MISMATCH
    assert wrong_dag.code is PolicyCode.AIRFLOW_DAG_DENIED
    assert exhausted.code is PolicyCode.BUDGET_DENIED


def test_observer_profile_cannot_trigger() -> None:
    decision = authorize_tool_call(
        OBSERVER,
        _request(role="airflow-observer"),
        ToolUsage(),
    )

    assert decision.code is PolicyCode.TOOL_DENIED
