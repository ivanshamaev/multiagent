from __future__ import annotations

import importlib.util
import json
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from urllib.parse import urlsplit
from urllib.request import Request

import pytest

SCRIPT_PATH = Path(__file__).parents[2] / "platform" / "airflow" / "scripts" / "api_smoke.py"
MODULE_NAME = "agentic_airflow_api_smoke"


def _load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location(MODULE_NAME, SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[MODULE_NAME] = module
    spec.loader.exec_module(module)
    return module


api_smoke = _load_script()


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


class SequenceTransport:
    def __init__(
        self,
        responses: list[tuple[str, str, int, object | None]],
        verifier: Callable[[Request], None] | None = None,
    ) -> None:
        self.responses = responses
        self.verifier = verifier
        self.calls: list[Request] = []

    def __call__(self, request: Request, timeout: float) -> tuple[int, bytes]:
        assert timeout == 7.0
        self.calls.append(request)
        assert self.responses, f"unexpected request {request.method} {request.full_url}"
        expected_method, expected_path, status, payload = self.responses.pop(0)
        assert request.method == expected_method
        parsed = urlsplit(request.full_url)
        actual_path = parsed.path + (f"?{parsed.query}" if parsed.query else "")
        assert actual_path == expected_path
        if self.verifier is not None:
            self.verifier(request)
        body = b"" if payload is None else json.dumps(payload).encode()
        return status, body


def _config(password: str = "unit-password") -> object:
    return api_smoke.Config(
        base_url="http://127.0.0.1:8080",
        username="unit-admin",
        password=password,
        request_timeout_seconds=7.0,
        poll_timeout_seconds=30.0,
        poll_interval_seconds=1.0,
    )


def _tasks(state: str = "success") -> list[dict[str, str]]:
    return [{"task_id": task_id, "state": state} for task_id in sorted(api_smoke.EXPECTED_TASK_IDS)]


def _task_definitions() -> list[dict[str, object]]:
    return [
        {
            "task_id": task_id,
            "downstream_task_ids": list(api_smoke.TASK_CHAIN[index + 1 : index + 2]),
        }
        for index, task_id in enumerate(api_smoke.TASK_CHAIN)
    ]


def test_run_smoke_uses_v2_contract_and_checks_all_tasks() -> None:
    run_id = "api_smoke_unit_001"
    token = "unit-jwt"
    task_definitions = _task_definitions()
    healthy = {
        "metadatabase": {"status": "healthy"},
        "scheduler": {"status": "healthy"},
        "dag_processor": {"status": "healthy"},
        "triggerer": {"status": None},
    }
    responses = [
        ("GET", "/api/v2/dags?limit=1", 401, {"detail": "Not authenticated"}),
        ("POST", "/auth/token", 201, {"access_token": token}),
        ("GET", "/api/v2/monitor/health", 200, healthy),
        ("GET", "/api/v2/dags/ecommerce_hourly", 404, {"detail": "Not found"}),
        ("GET", "/api/v2/dags/ecommerce_hourly", 200, {"dag_id": "ecommerce_hourly"}),
        ("GET", "/api/v2/dags/ecommerce_hourly/tasks?limit=100", 200, {"tasks": task_definitions}),
        (
            "POST",
            "/api/v2/dags/ecommerce_hourly/dagRuns",
            200,
            {"dag_id": "ecommerce_hourly", "dag_run_id": run_id, "state": "queued"},
        ),
        (
            "GET",
            f"/api/v2/dags/ecommerce_hourly/dagRuns/{run_id}",
            200,
            {"dag_id": "ecommerce_hourly", "dag_run_id": run_id, "state": "running"},
        ),
        (
            "GET",
            f"/api/v2/dags/ecommerce_hourly/dagRuns/{run_id}",
            200,
            {"dag_id": "ecommerce_hourly", "dag_run_id": run_id, "state": "success"},
        ),
        (
            "GET",
            f"/api/v2/dags/ecommerce_hourly/dagRuns/{run_id}/taskInstances?limit=100",
            200,
            {"task_instances": _tasks()},
        ),
    ]

    def verify_request(request: Request) -> None:
        path = urlsplit(request.full_url).path
        authorization = request.get_header("Authorization")
        if path in {"/auth/token", "/api/v2/monitor/health", "/api/v2/dags"}:
            assert authorization is None
        else:
            assert authorization == f"Bearer {token}"
        if path == "/auth/token":
            assert json.loads(request.data) == {
                "username": "unit-admin",
                "password": "unit-password",
            }
        if path.endswith("/dagRuns"):
            assert json.loads(request.data) == {
                "dag_run_id": run_id,
                "logical_date": None,
                "conf": {"source": "api_smoke"},
            }

    transport = SequenceTransport(responses, verify_request)
    clock = FakeClock()

    api_smoke.run_smoke(
        _config(),
        transport=transport,
        monotonic=clock.monotonic,
        sleep=clock.sleep,
        run_id_factory=lambda: run_id,
    )

    assert not transport.responses
    assert clock.now == 2.0


def test_run_smoke_fails_immediately_when_dag_run_fails() -> None:
    run_id = "api_smoke_unit_failed"
    healthy = {
        component: {"status": "healthy"}
        for component in ("metadatabase", "scheduler", "dag_processor")
    }
    task_definitions = _task_definitions()
    responses = [
        ("GET", "/api/v2/dags?limit=1", 401, {}),
        ("POST", "/auth/token", 201, {"access_token": "unit-jwt"}),
        ("GET", "/api/v2/monitor/health", 200, healthy),
        ("GET", "/api/v2/dags/ecommerce_hourly", 200, {"dag_id": "ecommerce_hourly"}),
        ("GET", "/api/v2/dags/ecommerce_hourly/tasks?limit=100", 200, {"tasks": task_definitions}),
        (
            "POST",
            "/api/v2/dags/ecommerce_hourly/dagRuns",
            200,
            {"dag_id": "ecommerce_hourly", "dag_run_id": run_id},
        ),
        (
            "GET",
            f"/api/v2/dags/ecommerce_hourly/dagRuns/{run_id}",
            200,
            {"state": "failed"},
        ),
    ]
    transport = SequenceTransport(responses)
    clock = FakeClock()

    with pytest.raises(api_smoke.SmokeError, match=r"DAG run .* failed"):
        api_smoke.run_smoke(
            _config(),
            transport=transport,
            monotonic=clock.monotonic,
            sleep=clock.sleep,
            run_id_factory=lambda: run_id,
        )

    assert not transport.responses
    assert clock.now == 0.0


def test_main_never_prints_password_or_jwt(capsys: pytest.CaptureFixture[str]) -> None:
    password = "never-print-this-password"
    token = "never-print-this-jwt"
    environ = {
        "AIRFLOW_API_BASE_URL": "http://127.0.0.1:8080",
        "AIRFLOW_ADMIN_USERNAME": "unit-admin",
        "AIRFLOW_ADMIN_PASSWORD": password,
        "AIRFLOW_API_REQUEST_TIMEOUT_SECONDS": "7",
        "AIRFLOW_API_POLL_TIMEOUT_SECONDS": "30",
        "AIRFLOW_API_POLL_INTERVAL_SECONDS": "1",
    }
    transport = SequenceTransport(
        [
            ("GET", "/api/v2/dags?limit=1", 401, {}),
            ("POST", "/auth/token", 201, {"access_token": token}),
            ("GET", "/api/v2/monitor/health", 503, {"detail": token}),
        ]
    )

    result = api_smoke.main(environ, transport=transport)

    captured = capsys.readouterr()
    assert result == 1
    assert "Airflow API smoke: FAIL:" in captured.err
    assert password not in captured.out + captured.err
    assert token not in captured.out + captured.err


def test_redirect_policy_does_not_create_a_forwarded_request() -> None:
    request = Request(
        "http://127.0.0.1:8080/api/v2/dags",
        headers={"Authorization": "Bearer never-forward-this-token"},
    )

    redirected = api_smoke.NoRedirects().redirect_request(
        request,
        None,
        302,
        "Found",
        {},
        "https://redirect-target.invalid/capture",
    )

    assert redirected is None


def test_poll_deadline_prevents_an_extra_request_and_bounds_timeout() -> None:
    clock = FakeClock()
    calls: list[float] = []

    def unhealthy_transport(request: Request, timeout: float) -> tuple[int, bytes]:
        calls.append(timeout)
        body = json.dumps(
            {
                "metadatabase": {"status": "healthy"},
                "scheduler": {"status": "unhealthy"},
                "dag_processor": {"status": "healthy"},
            }
        ).encode()
        return 200, body

    deadline = 1.0
    client = api_smoke.AirflowApiClient(
        "http://127.0.0.1:8080",
        request_timeout_seconds=7.0,
        transport=unhealthy_transport,
        deadline=deadline,
        monotonic=clock.monotonic,
    )

    with pytest.raises(api_smoke.SmokeError, match="overall deadline"):
        api_smoke._wait_for_health(
            client,
            deadline,
            interval_seconds=1.0,
            monotonic=clock.monotonic,
            sleep=clock.sleep,
        )

    assert calls == [1.0]
    assert clock.now == deadline


def test_invalid_run_state_is_not_reflected_in_the_error() -> None:
    reflected_secret = "never-reflect-this-secret"
    run_id = "api_smoke_invalid_state"
    clock = FakeClock()
    transport = SequenceTransport(
        [
            (
                "GET",
                f"/api/v2/dags/ecommerce_hourly/dagRuns/{run_id}",
                200,
                {"state": reflected_secret},
            )
        ]
    )
    client = api_smoke.AirflowApiClient(
        "http://127.0.0.1:8080",
        request_timeout_seconds=7.0,
        transport=transport,
        deadline=30.0,
        monotonic=clock.monotonic,
    )

    with pytest.raises(api_smoke.SmokeError) as exc_info:
        api_smoke._wait_for_run(
            client,
            "unit-jwt",
            run_id,
            deadline=30.0,
            interval_seconds=1.0,
            monotonic=clock.monotonic,
            sleep=clock.sleep,
        )

    assert reflected_secret not in str(exc_info.value)
    assert not transport.responses


def test_task_contract_rejects_a_changed_dependency_edge() -> None:
    tasks = _task_definitions()
    tasks[0]["downstream_task_ids"] = []

    with pytest.raises(api_smoke.SmokeError, match="dependencies differ"):
        api_smoke._extract_task_ids({"tasks": tasks}, "Airflow task discovery")


def test_task_contract_rejects_duplicate_task_ids() -> None:
    tasks = _task_definitions()
    tasks.append(dict(tasks[0]))

    with pytest.raises(api_smoke.SmokeError, match="duplicate tasks"):
        api_smoke._extract_task_ids({"tasks": tasks}, "Airflow task discovery")


def test_plain_http_base_url_is_rejected_outside_loopback() -> None:
    with pytest.raises(api_smoke.SmokeError, match="requires HTTPS"):
        api_smoke._validate_base_url("http://airflow.example.test:8080")
