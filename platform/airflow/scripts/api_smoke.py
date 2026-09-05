#!/usr/bin/env python3
"""Run the deterministic Airflow public API acceptance smoke."""

from __future__ import annotations

import json
import math
import os
import sys
import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

DAG_ID = "ecommerce_hourly"
FAILURE_PROBE_DAG_ID = "ecommerce_failure_probe"
PROBE_DAG_ID = FAILURE_PROBE_DAG_ID
TASK_CHAIN = (
    "load_raw",
    "dbt_staging",
    "dbt_intermediate",
    "dbt_marts",
    "dbt_tests",
    "publish",
)
EXPECTED_TASK_IDS = frozenset(TASK_CHAIN)

DEFAULT_REQUEST_TIMEOUT_SECONDS = 10.0
DEFAULT_POLL_TIMEOUT_SECONDS = 300.0
DEFAULT_POLL_INTERVAL_SECONDS = 2.0
DEFAULT_CLEANUP_TIMEOUT_SECONDS = 10.0


class SmokeError(RuntimeError):
    """An expected, safely reportable acceptance-smoke failure."""


class Transport(Protocol):
    """Minimal injectable HTTP transport used by the API client."""

    def __call__(self, request: Request, timeout: float) -> tuple[int, bytes]: ...


@dataclass(frozen=True, slots=True)
class Config:
    """Validated runtime configuration loaded from the environment."""

    base_url: str
    username: str = field(repr=False)
    password: str = field(repr=False)
    request_timeout_seconds: float = DEFAULT_REQUEST_TIMEOUT_SECONDS
    poll_timeout_seconds: float = DEFAULT_POLL_TIMEOUT_SECONDS
    poll_interval_seconds: float = DEFAULT_POLL_INTERVAL_SECONDS

    @classmethod
    def from_env(cls, environ: Mapping[str, str]) -> Config:
        """Create configuration without copying or displaying credentials."""
        base_url = _required_env(environ, "AIRFLOW_API_BASE_URL").rstrip("/")
        username = _required_env(environ, "AIRFLOW_ADMIN_USERNAME")
        password = _required_env(environ, "AIRFLOW_ADMIN_PASSWORD", strip=False)
        _validate_base_url(base_url)

        return cls(
            base_url=base_url,
            username=username,
            password=password,
            request_timeout_seconds=_positive_float_env(
                environ,
                "AIRFLOW_API_REQUEST_TIMEOUT_SECONDS",
                DEFAULT_REQUEST_TIMEOUT_SECONDS,
            ),
            poll_timeout_seconds=_positive_float_env(
                environ,
                "AIRFLOW_API_POLL_TIMEOUT_SECONDS",
                DEFAULT_POLL_TIMEOUT_SECONDS,
            ),
            poll_interval_seconds=_positive_float_env(
                environ,
                "AIRFLOW_API_POLL_INTERVAL_SECONDS",
                DEFAULT_POLL_INTERVAL_SECONDS,
            ),
        )


@dataclass(frozen=True, slots=True)
class JsonResponse:
    """HTTP status and decoded JSON response body."""

    status: int
    payload: object | None


class AirflowApiClient:
    """Small OpenAPI-v2 client with an injectable stdlib transport."""

    def __init__(
        self,
        base_url: str,
        request_timeout_seconds: float,
        transport: Transport,
        deadline: float,
        monotonic: Callable[[], float],
    ) -> None:
        self._base_url = base_url
        self._request_timeout_seconds = request_timeout_seconds
        self._transport = transport
        self._deadline = deadline
        self._monotonic = monotonic

    def request_json(
        self,
        method: str,
        path: str,
        *,
        payload: Mapping[str, object] | None = None,
        token: str | None = None,
    ) -> JsonResponse:
        """Send one JSON request without exposing request headers in errors."""
        data = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(payload, separators=(",", ":")).encode()
            headers["Content-Type"] = "application/json"
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"

        request = Request(
            f"{self._base_url}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            remaining = self._deadline - self._monotonic()
            if remaining <= 0:
                raise SmokeError("Airflow API smoke exceeded its overall deadline")
            status, body = self._transport(request, min(self._request_timeout_seconds, remaining))
            if self._monotonic() >= self._deadline:
                raise SmokeError("Airflow API smoke exceeded its overall deadline")
        except (TimeoutError, URLError, OSError) as exc:
            raise SmokeError(f"{method} {path} failed ({type(exc).__name__})") from None

        if not body:
            return JsonResponse(status=status, payload=None)

        try:
            decoded = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            if 200 <= status < 300:
                raise SmokeError(f"{method} {path} returned invalid JSON") from None
            decoded = None
        return JsonResponse(status=status, payload=decoded)


class NoRedirects(HTTPRedirectHandler):
    """Keep login payloads and bearer tokens on the configured API origin."""

    def redirect_request(
        self,
        req: Request,
        fp: object,
        code: int,
        msg: str,
        headers: object,
        newurl: str,
    ) -> None:
        return None


def _stdlib_transport(request: Request, timeout: float) -> tuple[int, bytes]:
    try:
        with build_opener(NoRedirects()).open(request, timeout=timeout) as response:
            return response.status, response.read()
    except HTTPError as exc:
        try:
            return exc.code, exc.read()
        finally:
            exc.close()


def _required_env(
    environ: Mapping[str, str],
    name: str,
    *,
    strip: bool = True,
) -> str:
    value = environ.get(name)
    if value is None or not value:
        raise SmokeError(f"required environment variable {name} is missing")
    normalized = value.strip() if strip else value
    if not normalized:
        raise SmokeError(f"required environment variable {name} is empty")
    return normalized


def _positive_float_env(environ: Mapping[str, str], name: str, default: float) -> float:
    raw_value = environ.get(name)
    if raw_value is None or not raw_value.strip():
        return default
    try:
        value = float(raw_value)
    except ValueError:
        raise SmokeError(f"environment variable {name} must be a number") from None
    if not math.isfinite(value) or value <= 0:
        raise SmokeError(f"environment variable {name} must be finite and greater than zero")
    return value


def _validate_base_url(base_url: str) -> None:
    parsed = urlsplit(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise SmokeError("AIRFLOW_API_BASE_URL must be an absolute HTTP(S) URL")
    if parsed.username is not None or parsed.password is not None:
        raise SmokeError("AIRFLOW_API_BASE_URL must not contain credentials")
    if parsed.query or parsed.fragment:
        raise SmokeError("AIRFLOW_API_BASE_URL must not contain a query or fragment")
    if parsed.scheme == "http" and parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise SmokeError("AIRFLOW_API_BASE_URL requires HTTPS outside loopback")


def _require_status(response: JsonResponse, expected: int, operation: str) -> None:
    if response.status != expected:
        raise SmokeError(f"{operation} returned HTTP {response.status}; expected {expected}")


def _require_object(payload: object | None, operation: str) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise SmokeError(f"{operation} returned an invalid JSON object")
    return payload


def _require_string(payload: Mapping[str, object], key: str, operation: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise SmokeError(f"{operation} response is missing {key}")
    return value


def _pause(
    deadline: float,
    interval_seconds: float,
    operation: str,
    monotonic: Callable[[], float],
    sleep: Callable[[float], None],
) -> None:
    remaining = deadline - monotonic()
    if remaining <= 0:
        raise SmokeError(f"timed out waiting for {operation}")
    sleep(min(interval_seconds, remaining))


def _wait_for_health(
    client: AirflowApiClient,
    deadline: float,
    interval_seconds: float,
    monotonic: Callable[[], float],
    sleep: Callable[[float], None],
) -> None:
    required_components = ("metadatabase", "scheduler", "dag_processor")
    while True:
        response = client.request_json("GET", "/api/v2/monitor/health")
        _require_status(response, 200, "Airflow health check")
        health = _require_object(response.payload, "Airflow health check")
        if all(
            isinstance(health.get(component), dict) and health[component].get("status") == "healthy"  # type: ignore[union-attr]
            for component in required_components
        ):
            return
        _pause(deadline, interval_seconds, "healthy Airflow components", monotonic, sleep)


def _extract_task_ids(payload: object | None, operation: str) -> frozenset[str]:
    body = _require_object(payload, operation)
    tasks = body.get("tasks")
    if not isinstance(tasks, list):
        raise SmokeError(f"{operation} response is missing tasks")

    task_ids: set[str] = set()
    for task in tasks:
        if not isinstance(task, dict) or not isinstance(task.get("task_id"), str):
            raise SmokeError(f"{operation} returned an invalid task entry")
        if task["task_id"] in task_ids:
            raise SmokeError(f"{operation} returned duplicate tasks")
        task_ids.add(task["task_id"])
        if task["task_id"] in EXPECTED_TASK_IDS:
            position = TASK_CHAIN.index(task["task_id"])
            expected = list(TASK_CHAIN[position + 1 : position + 2])
            if task.get("downstream_task_ids") != expected:
                raise SmokeError("Airflow DAG task dependencies differ from the baseline chain")
    return frozenset(task_ids)


def _wait_for_dag_contract(
    client: AirflowApiClient,
    token: str,
    deadline: float,
    interval_seconds: float,
    monotonic: Callable[[], float],
    sleep: Callable[[float], None],
    dag_id: str = DAG_ID,
) -> None:
    dag_path = f"/api/v2/dags/{quote(dag_id, safe='')}"
    while True:
        dag_response = client.request_json("GET", dag_path, token=token)
        if dag_response.status == 200:
            _require_object(dag_response.payload, "Airflow DAG discovery")
            tasks_response = client.request_json(
                "GET",
                f"{dag_path}/tasks?limit=100",
                token=token,
            )
            _require_status(tasks_response, 200, "Airflow task discovery")
            if (
                _extract_task_ids(tasks_response.payload, "Airflow task discovery")
                == EXPECTED_TASK_IDS
            ):
                return
        elif dag_response.status != 404:
            _require_status(dag_response, 200, "Airflow DAG discovery")
        _pause(deadline, interval_seconds, "the exact Airflow DAG contract", monotonic, sleep)


def _new_run_id() -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    return f"api_smoke_{timestamp}_{uuid.uuid4().hex[:8]}"


def _wait_for_run(
    client: AirflowApiClient,
    token: str,
    run_id: str,
    deadline: float,
    interval_seconds: float,
    monotonic: Callable[[], float],
    sleep: Callable[[float], None],
    dag_id: str = DAG_ID,
    expect_failure: bool = False,
) -> None:
    encoded_dag_id = quote(dag_id, safe="")
    encoded_run_id = quote(run_id, safe="")
    run_path = f"/api/v2/dags/{encoded_dag_id}/dagRuns/{encoded_run_id}"
    while True:
        response = client.request_json("GET", run_path, token=token)
        _require_status(response, 200, "Airflow DAG run lookup")
        run = _require_object(response.payload, "Airflow DAG run lookup")
        state = run.get("state")
        if state == "success":
            if expect_failure:
                raise SmokeError("failure probe unexpectedly succeeded")
            _verify_task_instances(client, token, run_path)
            _verify_publication(client, token, run_path, run_id)
            return
        if state == "failed":
            if not expect_failure:
                raise SmokeError(f"Airflow DAG run {run_id} failed")
            _verify_failure_task_instances(client, token, run_path)
            return
        if state not in {"queued", "running"}:
            raise SmokeError("Airflow DAG run returned an invalid state")
        _pause(deadline, interval_seconds, "Airflow DAG run success", monotonic, sleep)


def _get_task_states(client: AirflowApiClient, token: str, run_path: str) -> dict[str, str]:
    response = client.request_json(
        "GET",
        f"{run_path}/taskInstances?limit=100",
        token=token,
    )
    _require_status(response, 200, "Airflow task instance lookup")
    body = _require_object(response.payload, "Airflow task instance lookup")
    instances = body.get("task_instances")
    if not isinstance(instances, list):
        raise SmokeError("Airflow task instance lookup response is missing task_instances")

    states: dict[str, str] = {}
    for instance in instances:
        if not isinstance(instance, dict):
            raise SmokeError("Airflow task instance lookup returned an invalid entry")
        task_id = instance.get("task_id")
        state = instance.get("state")
        if not isinstance(task_id, str) or not isinstance(state, str):
            raise SmokeError("Airflow task instance lookup returned an invalid entry")
        if task_id in states:
            raise SmokeError(f"Airflow task instance lookup returned duplicate task {task_id}")
        states[task_id] = state

    if frozenset(states) != EXPECTED_TASK_IDS:
        raise SmokeError("Airflow DAG run did not contain the exact six task instances")
    return states


def _verify_task_instances(client: AirflowApiClient, token: str, run_path: str) -> None:
    states = _get_task_states(client, token, run_path)
    unsuccessful = sorted(task_id for task_id, state in states.items() if state != "success")
    if unsuccessful:
        raise SmokeError(
            f"Airflow DAG run has unsuccessful task instances: {', '.join(unsuccessful)}"
        )


def _verify_failure_task_instances(client: AirflowApiClient, token: str, run_path: str) -> None:
    states = _get_task_states(client, token, run_path)
    expected = {
        **dict.fromkeys(TASK_CHAIN[:4], "success"),
        "dbt_tests": "failed",
        "publish": "upstream_failed",
    }
    if states != expected:
        raise SmokeError("failure probe returned unexpected task states")


def _verify_publication(client: AirflowApiClient, token: str, run_path: str, run_id: str) -> None:
    response = client.request_json(
        "GET", f"{run_path}/taskInstances/publish/xcomEntries/return_value", token=token
    )
    _require_status(response, 200, "Airflow publish evidence lookup")
    body = _require_object(response.payload, "Airflow publish evidence lookup")
    value = body.get("value")
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            raise SmokeError("Airflow publish evidence is invalid JSON") from None
    evidence = _require_object(value, "Airflow publish evidence")
    invocations = evidence.get("invocation_ids")
    if (
        evidence.get("published") is not True
        or evidence.get("runner") != "dbt-subprocess-v1"
        or evidence.get("run_id") != run_id
        or evidence.get("stages") != list(TASK_CHAIN[:-1])
        or not isinstance(invocations, list)
        or len(invocations) != 5
        or any(not isinstance(item, str) or not item for item in invocations)
        or len(set(invocations)) != 5
    ):
        raise SmokeError("Airflow publish evidence does not prove five current-run dbt invocations")


def _set_pause(client: AirflowApiClient, token: str, dag_id: str, is_paused: bool) -> None:
    path = f"/api/v2/dags/{quote(dag_id, safe='')}"
    response = client.request_json("PATCH", path, payload={"is_paused": is_paused}, token=token)
    _require_status(response, 200, "Airflow DAG pause update")
    body = _require_object(response.payload, "Airflow DAG pause update")
    if body.get("is_paused") is not is_paused:
        raise SmokeError("Airflow DAG pause update did not confirm the requested state")


def _read_pause(client: AirflowApiClient, token: str, dag_id: str) -> bool:
    path = f"/api/v2/dags/{quote(dag_id, safe='')}"
    response = client.request_json("GET", path, token=token)
    _require_status(response, 200, "Airflow DAG pause lookup")
    dag = _require_object(response.payload, "Airflow DAG pause lookup")
    paused = dag.get("is_paused")
    if not isinstance(paused, bool):
        raise SmokeError("Airflow DAG pause lookup returned an invalid flag")
    return paused


def run_smoke(
    config: Config,
    *,
    transport: Transport = _stdlib_transport,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
    run_id_factory: Callable[[], str] = _new_run_id,
    dag_id: str = DAG_ID,
    expect_failure: bool = False,
) -> str:
    """Execute the complete authenticated Airflow API acceptance contract."""
    if dag_id not in {DAG_ID, FAILURE_PROBE_DAG_ID}:
        raise SmokeError("DAG is not in the Airflow API smoke allowlist")
    if expect_failure != (dag_id == FAILURE_PROBE_DAG_ID):
        raise SmokeError("Airflow smoke DAG and expected outcome do not match")
    deadline = monotonic() + config.poll_timeout_seconds
    client = AirflowApiClient(
        config.base_url,
        config.request_timeout_seconds,
        transport,
        deadline,
        monotonic,
    )

    unauthenticated = client.request_json("GET", "/api/v2/dags?limit=1")
    _require_status(unauthenticated, 401, "Unauthenticated Airflow API check")

    token_response = client.request_json(
        "POST",
        "/auth/token",
        payload={"username": config.username, "password": config.password},
    )
    _require_status(token_response, 201, "Airflow token request")
    token = _require_string(
        _require_object(token_response.payload, "Airflow token request"),
        "access_token",
        "Airflow token request",
    )

    _wait_for_health(
        client,
        deadline,
        config.poll_interval_seconds,
        monotonic,
        sleep,
    )
    _wait_for_dag_contract(
        client, token, deadline, config.poll_interval_seconds, monotonic, sleep, dag_id
    )
    previous_paused = _read_pause(client, token, dag_id)
    try:
        _set_pause(client, token, dag_id, False)
        run_id = run_id_factory()
        trigger_response = client.request_json(
            "POST",
            f"/api/v2/dags/{quote(dag_id, safe='')}/dagRuns",
            payload={"dag_run_id": run_id, "logical_date": None, "conf": {"source": "api_smoke"}},
            token=token,
        )
        _require_status(trigger_response, 200, "Airflow DAG trigger")
        triggered_run = _require_object(trigger_response.payload, "Airflow DAG trigger")
        if triggered_run.get("dag_id") != dag_id or triggered_run.get("dag_run_id") != run_id:
            raise SmokeError("Airflow DAG trigger returned a different run identity")
        _wait_for_run(
            client,
            token,
            run_id,
            deadline,
            config.poll_interval_seconds,
            monotonic,
            sleep,
            dag_id,
            expect_failure,
        )
        return run_id
    finally:
        cleanup_deadline = monotonic() + min(
            DEFAULT_CLEANUP_TIMEOUT_SECONDS, config.request_timeout_seconds
        )
        cleanup_client = AirflowApiClient(
            config.base_url,
            config.request_timeout_seconds,
            transport,
            cleanup_deadline,
            monotonic,
        )
        try:
            _set_pause(cleanup_client, token, dag_id, previous_paused)
        except SmokeError:
            raise SmokeError(
                "failed to restore the previous DAG pause state; check it manually"
            ) from None


def main(
    environ: Mapping[str, str] | None = None,
    *,
    transport: Transport = _stdlib_transport,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
    run_id_factory: Callable[[], str] = _new_run_id,
    argv: list[str] | None = None,
) -> int:
    """CLI entrypoint with deliberately secret-free output."""
    try:
        config = Config.from_env(os.environ if environ is None else environ)
        args = [] if argv is None else argv
        if any(arg != "--expect-failure" for arg in args):
            raise SmokeError("usage: api_smoke.py [--expect-failure]")
        expect_failure = "--expect-failure" in args
        selected_dag = FAILURE_PROBE_DAG_ID if expect_failure else DAG_ID
        run_id = run_smoke(
            config,
            transport=transport,
            monotonic=monotonic,
            sleep=sleep,
            run_id_factory=run_id_factory,
            dag_id=selected_dag,
            expect_failure=expect_failure,
        )
    except SmokeError as exc:
        print(f"Airflow API smoke: FAIL: {exc}", file=sys.stderr)
        return 1

    result = "expected failure" if expect_failure else "6/6 success"
    print(f"Airflow API smoke: PASS; dag={selected_dag}; run_id={run_id}; tasks={result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(argv=sys.argv[1:]))
