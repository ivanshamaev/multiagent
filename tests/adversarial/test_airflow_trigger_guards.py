from pathlib import Path

import pytest
from pydantic import ValidationError

from contracts import ToolRequest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "extra",
    [
        {"conf": {"secret": "value"}},
        {"run_id": "attacker-selected"},
        {"method": "DELETE"},
        {"url": "https://example.test"},
        {"logical_date": "2026-09-13T00:00:00Z"},
    ],
)
def test_trigger_contract_rejects_caller_controlled_http_and_run_fields(
    extra: dict[str, object],
) -> None:
    call: dict[str, object] = {
        "tool": "airflow.trigger_dag",
        "task_id": "task-airflow-trigger",
        "dag_id": "ecommerce_acceptance",
        "idempotency_key": "release-20260913",
        "approval_id": "airflow-approval-unit",
    }
    call.update(extra)

    with pytest.raises(ValidationError):
        ToolRequest(
            request_id="request-airflow-trigger",
            task_id="task-airflow-trigger",
            actor_id="airflow-trigger-agent",
            role="airflow-trigger-controller",
            call=call,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("value", ["short", "../escape-value", "key with spaces", "key?query=yes"])
def test_idempotency_key_is_closed_and_bounded(value: str) -> None:
    with pytest.raises(ValidationError):
        ToolRequest(
            request_id="request-airflow-trigger",
            task_id="task-airflow-trigger",
            actor_id="airflow-trigger-agent",
            role="airflow-trigger-controller",
            call={
                "tool": "airflow.trigger_dag",
                "task_id": "task-airflow-trigger",
                "dag_id": "ecommerce_acceptance",
                "idempotency_key": value,
                "approval_id": "airflow-approval-unit",
            },
        )
