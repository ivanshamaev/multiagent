import asyncio
import json
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request

import pytest

from contracts import AirflowGetTaskLogCall, ToolCallStatus, ToolRequest
from policies import load_capability_profile
from runtime.tools import (
    AirflowAPIAdapter,
    AirflowAPIConfig,
    AirflowAPIError,
    AirflowMCPTools,
    MCPToolGateway,
    ToolEvidenceStore,
)

ROOT = Path(__file__).resolve().parents[2]


class SequenceTransport:
    def __init__(self, responses: list[tuple[str, str, int, object]]) -> None:
        self.responses = responses
        self.requests: list[Request] = []

    def __call__(self, request: Request, timeout: float, max_bytes: int) -> tuple[int, bytes]:
        assert timeout == 7
        assert max_bytes == 1_000
        self.requests.append(request)
        method, path, status, payload = self.responses.pop(0)
        parsed = urlsplit(request.full_url)
        actual = parsed.path + (f"?{parsed.query}" if parsed.query else "")
        assert request.method == method
        assert actual == path
        return status, json.dumps(payload).encode()


class RecordingCaller:
    def __init__(self, result: str = "{}") -> None:
        self.result = result
        self.calls: list[tuple[str, dict[str, object]]] = []

    async def call_tool(self, tool_name: str, **kwargs: object) -> str:
        self.calls.append((tool_name, kwargs))
        return self.result


def _config(**updates: object) -> AirflowAPIConfig:
    values = {
        "base_url": "http://127.0.0.1:8080",
        "username": "observer",
        "password": "secret-password",
        "allowed_dags": frozenset({"ecommerce_acceptance"}),
        "timeout_seconds": 7,
        "max_response_bytes": 1_000,
    }
    values.update(updates)
    return AirflowAPIConfig(**values)  # type: ignore[arg-type]


def test_api_adapter_authenticates_once_filters_dags_and_uses_get_only() -> None:
    transport = SequenceTransport(
        [
            ("POST", "/auth/token", 201, {"access_token": "unit-jwt"}),
            (
                "GET",
                "/api/v2/dags?limit=100&offset=0",
                200,
                {
                    "dags": [
                        {"dag_id": "ecommerce_acceptance"},
                        {"dag_id": "private_dag"},
                    ],
                    "total_entries": 2,
                },
            ),
            (
                "GET",
                "/api/v2/dags/ecommerce_acceptance",
                200,
                {"dag_id": "ecommerce_acceptance", "is_paused": True},
            ),
        ]
    )
    adapter = AirflowAPIAdapter(_config(), transport=transport)

    listed = json.loads(
        adapter.execute(
            ToolRequest.model_validate(
                {
                    "request_id": "r1",
                    "task_id": "t1",
                    "actor_id": "a1",
                    "role": "airflow-observer",
                    "call": {"tool": "airflow.list_dags"},
                }
            ).call
        )
    )
    detail = json.loads(
        adapter.execute(
            ToolRequest.model_validate(
                {
                    "request_id": "r2",
                    "task_id": "t1",
                    "actor_id": "a1",
                    "role": "airflow-observer",
                    "call": {"tool": "airflow.get_dag", "dag_id": "ecommerce_acceptance"},
                }
            ).call
        )
    )

    assert listed == {"dags": [{"dag_id": "ecommerce_acceptance"}], "total_entries": 1}
    assert detail["is_paused"] is True
    assert not transport.responses
    assert json.loads(transport.requests[0].data) == {
        "username": "observer",
        "password": "secret-password",
    }
    assert transport.requests[1].get_header("Authorization") == "Bearer unit-jwt"
    assert all(request.method == "GET" for request in transport.requests[1:])


def test_api_adapter_encodes_ids_and_bounds_log_parameters() -> None:
    transport = SequenceTransport(
        [
            ("POST", "/auth/token", 201, {"access_token": "unit-jwt"}),
            (
                "GET",
                (
                    "/api/v2/dags/ecommerce_acceptance/dagRuns/"
                    "scheduled__2026-09-13T00%3A00%3A00%2B00%3A00/taskInstances/"
                    "dbt.fct_orders_run/logs/1?full_content=false&map_index=-1"
                ),
                200,
                {"content": "bounded", "continuation_token": None},
            ),
        ]
    )
    adapter = AirflowAPIAdapter(_config(), transport=transport)
    call = AirflowGetTaskLogCall(
        dag_id="ecommerce_acceptance",
        dag_run_id="scheduled__2026-09-13T00:00:00+00:00",
        task_id="dbt.fct_orders_run",
        try_number=1,
    )

    assert json.loads(adapter.execute(call))["content"] == "bounded"
    assert not transport.responses


def test_api_adapter_removes_conf_and_internal_execution_metadata() -> None:
    transport = SequenceTransport(
        [
            ("POST", "/auth/token", 201, {"access_token": "unit-jwt"}),
            (
                "GET",
                "/api/v2/dags/ecommerce_acceptance/dagRuns?limit=1&offset=0&order_by=-id",
                200,
                {
                    "dag_runs": [
                        {
                            "dag_id": "ecommerce_acceptance",
                            "dag_run_id": "manual__one",
                            "state": "success",
                            "conf": {"credential": "must-not-pass"},
                        }
                    ],
                    "total_entries": 1,
                },
            ),
            (
                "GET",
                (
                    "/api/v2/dags/ecommerce_acceptance/dagRuns/manual__one/"
                    "taskInstances?limit=100&offset=0"
                ),
                200,
                {
                    "task_instances": [
                        {
                            "dag_id": "ecommerce_acceptance",
                            "dag_run_id": "manual__one",
                            "task_id": "publish",
                            "state": "success",
                            "try_number": 1,
                            "executor_config": {"secret": "must-not-pass"},
                        }
                    ],
                    "total_entries": 1,
                },
            ),
        ]
    )
    adapter = AirflowAPIAdapter(_config(), transport=transport)
    runs = json.loads(
        adapter.execute(
            ToolRequest.model_validate(
                {
                    "request_id": "r1",
                    "task_id": "t1",
                    "actor_id": "a1",
                    "role": "airflow-observer",
                    "call": {
                        "tool": "airflow.list_dag_runs",
                        "dag_id": "ecommerce_acceptance",
                        "limit": 1,
                    },
                }
            ).call
        )
    )
    tasks = json.loads(
        adapter.execute(
            ToolRequest.model_validate(
                {
                    "request_id": "r2",
                    "task_id": "t1",
                    "actor_id": "a1",
                    "role": "airflow-observer",
                    "call": {
                        "tool": "airflow.list_task_instances",
                        "dag_id": "ecommerce_acceptance",
                        "dag_run_id": "manual__one",
                    },
                }
            ).call
        )
    )

    assert "conf" not in runs["dag_runs"][0]
    assert "executor_config" not in tasks["task_instances"][0]
    assert "must-not-pass" not in json.dumps({"runs": runs, "tasks": tasks})


def test_api_adapter_errors_are_bounded_and_secret_free() -> None:
    def oversized(request: Request, timeout: float, max_bytes: int) -> tuple[int, bytes]:
        return 200, b"x" * (max_bytes + 1)

    adapter = AirflowAPIAdapter(_config(), transport=oversized)

    with pytest.raises(AirflowAPIError, match="byte limit") as captured:
        adapter.execute(
            ToolRequest.model_validate(
                {
                    "request_id": "r1",
                    "task_id": "t1",
                    "actor_id": "a1",
                    "role": "airflow-observer",
                    "call": {"tool": "airflow.list_dags"},
                }
            ).call
        )

    assert "secret-password" not in str(captured.value)


def test_airflow_facade_routes_through_policy_and_retains_evidence(tmp_path: Path) -> None:
    profile = load_capability_profile(ROOT / "policies/profiles/airflow_observer_v1.json")
    caller = RecordingCaller('{"dag_id":"ecommerce_acceptance"}')
    gateway = MCPToolGateway(
        profile,
        None,
        None,
        ToolEvidenceStore(tmp_path, tmp_path / ".scenario-state"),
        airflow=caller,
    )
    facade = AirflowMCPTools(
        gateway,
        task_id="task-airflow-observe",
        actor_id="airflow-observer-agent",
    )
    get_dag = next(tool for tool in facade.tools if tool.name == "airflow_get_dag")

    result = asyncio.run(get_dag.invoke(arguments={"dag_id": "ecommerce_acceptance"}))

    assert result[0].text == '{"dag_id":"ecommerce_acceptance"}'
    assert caller.calls == [("get_dag", {"dag_id": "ecommerce_acceptance"})]
    assert gateway.evidence[0].status is ToolCallStatus.SUCCESS
    assert gateway.evidence[0].task_id == "task-airflow-observe"
