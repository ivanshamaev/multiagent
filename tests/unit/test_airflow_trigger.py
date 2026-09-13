from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request

import pytest

from contracts import AirflowTriggerDagCall, ToolCallStatus, ToolRequest
from policies import load_capability_profile
from runtime.tools import (
    AirflowApprovalError,
    AirflowApprovalStore,
    AirflowTriggerAdapter,
    AirflowTriggerConfig,
    AirflowTriggerError,
    AirflowTriggerMCPTools,
    MCPToolGateway,
    ToolEvidenceStore,
)

ROOT = Path(__file__).resolve().parents[2]


class RecordingCaller:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    async def call_tool(self, tool_name: str, **kwargs: object) -> str:
        self.calls.append((tool_name, kwargs))
        return '{"dag_id":"ecommerce_acceptance","trigger_outcome":"created"}'


class Clock:
    def __init__(self) -> None:
        self.value = datetime(2026, 9, 13, 12, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.value


class SequenceTransport:
    def __init__(self, responses: list[tuple[str, str, int | Exception, object]]) -> None:
        self.responses = responses
        self.requests: list[Request] = []

    def __call__(self, request: Request, timeout: float, max_bytes: int) -> tuple[int, bytes]:
        assert timeout == 7
        assert max_bytes == 5_000
        self.requests.append(request)
        method, path, status, payload = self.responses.pop(0)
        assert request.method == method
        assert urlsplit(request.full_url).path == path
        if isinstance(status, Exception):
            raise status
        return status, json.dumps(payload).encode()


def _config(root: Path) -> AirflowTriggerConfig:
    return AirflowTriggerConfig(
        repository_root=root,
        approval_root=root / ".scenario-state/airflow-trigger-approvals",
        base_url="http://127.0.0.1:8080",
        username="trigger-user",
        password="secret-password",
        timeout_seconds=7,
        max_response_bytes=5_000,
    )


def _call(approval_id: str, *, key: str = "release-20260913") -> AirflowTriggerDagCall:
    return AirflowTriggerDagCall(
        task_id="task-airflow-trigger",
        dag_id="ecommerce_acceptance",
        idempotency_key=key,
        approval_id=approval_id,
    )


def _approval(store: AirflowApprovalStore, *, key: str = "release-20260913") -> str:
    return store.create(
        task_id="task-airflow-trigger",
        dag_id="ecommerce_acceptance",
        idempotency_key=key,
        approved_by="local-human",
    ).approval_id


def _run_payload(run_id: str) -> dict[str, object]:
    return {
        "dag_id": "ecommerce_acceptance",
        "dag_run_id": run_id,
        "state": "queued",
        "conf": {"must": "not pass"},
    }


def test_trigger_consumes_approval_and_sends_fixed_body(tmp_path: Path) -> None:
    clock = Clock()
    store = AirflowApprovalStore(tmp_path, clock=clock)
    approval_id = _approval(store)
    run_id = AirflowTriggerAdapter.run_id("ecommerce_acceptance", "release-20260913")
    transport = SequenceTransport(
        [
            ("POST", "/auth/token", 201, {"access_token": "jwt"}),
            ("GET", f"/api/v2/dags/ecommerce_acceptance/dagRuns/{run_id}", 404, {}),
            ("POST", "/api/v2/dags/ecommerce_acceptance/dagRuns", 200, _run_payload(run_id)),
        ]
    )
    adapter = AirflowTriggerAdapter(_config(tmp_path), transport=transport, approvals=store)

    result = json.loads(adapter.execute(_call(approval_id)))

    assert result["trigger_outcome"] == "created"
    assert "conf" not in result
    assert json.loads(transport.requests[2].data) == {
        "conf": {},
        "dag_run_id": run_id,
        "logical_date": None,
    }
    with pytest.raises(AirflowTriggerError, match="already"):
        adapter.execute(_call(approval_id))


def test_new_approval_same_key_returns_existing_without_post(tmp_path: Path) -> None:
    store = AirflowApprovalStore(tmp_path, clock=Clock())
    approval_id = _approval(store)
    run_id = AirflowTriggerAdapter.run_id("ecommerce_acceptance", "release-20260913")
    transport = SequenceTransport(
        [
            ("POST", "/auth/token", 201, {"access_token": "jwt"}),
            (
                "GET",
                f"/api/v2/dags/ecommerce_acceptance/dagRuns/{run_id}",
                200,
                _run_payload(run_id),
            ),
        ]
    )

    result = json.loads(
        AirflowTriggerAdapter(_config(tmp_path), transport=transport, approvals=store).execute(
            _call(approval_id)
        )
    )

    assert result["trigger_outcome"] == "existing"
    assert [request.method for request in transport.requests] == ["POST", "GET"]


def test_timeout_after_post_is_reconciled_before_return(tmp_path: Path) -> None:
    store = AirflowApprovalStore(tmp_path, clock=Clock())
    approval_id = _approval(store)
    run_id = AirflowTriggerAdapter.run_id("ecommerce_acceptance", "release-20260913")
    transport = SequenceTransport(
        [
            ("POST", "/auth/token", 201, {"access_token": "jwt"}),
            ("GET", f"/api/v2/dags/ecommerce_acceptance/dagRuns/{run_id}", 404, {}),
            ("POST", "/api/v2/dags/ecommerce_acceptance/dagRuns", TimeoutError(), {}),
            (
                "GET",
                f"/api/v2/dags/ecommerce_acceptance/dagRuns/{run_id}",
                200,
                _run_payload(run_id),
            ),
        ]
    )

    result = json.loads(
        AirflowTriggerAdapter(_config(tmp_path), transport=transport, approvals=store).execute(
            _call(approval_id)
        )
    )

    assert result["dag_run_id"] == run_id
    assert result["trigger_outcome"] == "created"


def test_expired_or_mismatched_approval_fails_before_network(tmp_path: Path) -> None:
    clock = Clock()
    store = AirflowApprovalStore(tmp_path, clock=clock)
    approval_id = _approval(store)
    transport = SequenceTransport([])
    adapter = AirflowTriggerAdapter(_config(tmp_path), transport=transport, approvals=store)

    with pytest.raises(AirflowTriggerError, match="does not match"):
        adapter.execute(_call(approval_id, key="different-key"))
    clock.value += timedelta(minutes=6)
    with pytest.raises(AirflowTriggerError, match="expired"):
        adapter.execute(_call(approval_id))
    assert transport.requests == []


def test_approval_store_rejects_external_or_symlink_root(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-approval-test"
    outside.mkdir(exist_ok=True)
    with pytest.raises(AirflowApprovalError, match="inside"):
        AirflowApprovalStore(tmp_path, outside)
    link = tmp_path / "approval-link"
    link.symlink_to(outside, target_is_directory=True)
    with pytest.raises(AirflowApprovalError, match="symlink"):
        AirflowApprovalStore(tmp_path, link)


def test_direct_gateway_still_checks_policy_and_retains_evidence(tmp_path: Path) -> None:
    profile = load_capability_profile(ROOT / "policies/profiles/airflow_trigger_v1.json")
    caller = RecordingCaller()
    gateway = MCPToolGateway(
        profile,
        None,
        None,
        ToolEvidenceStore(tmp_path, tmp_path / ".scenario-state"),
        airflow=caller,
    )
    request = ToolRequest(
        request_id="request-airflow-trigger",
        task_id="task-airflow-trigger",
        actor_id="airflow-trigger-agent",
        role="airflow-trigger-controller",
        call=_call("airflow-approval-unit"),
    )

    result = asyncio.run(gateway.execute(request))

    assert "created" in result.content
    assert caller.calls[0][0] == "trigger_dag"
    assert caller.calls[0][1]["task_id"] == request.task_id
    assert gateway.evidence[0].status is ToolCallStatus.SUCCESS


def test_maf_trigger_facade_is_always_require(tmp_path: Path) -> None:
    profile = load_capability_profile(ROOT / "policies/profiles/airflow_trigger_v1.json")
    gateway = MCPToolGateway(
        profile,
        None,
        None,
        ToolEvidenceStore(tmp_path, tmp_path / ".scenario-state"),
        airflow=RecordingCaller(),
    )
    facade = AirflowTriggerMCPTools(
        gateway,
        task_id="task-airflow-trigger",
        actor_id="airflow-trigger-agent",
    )

    assert len(facade.tools) == 1
    assert facade.tools[0].approval_mode == "always_require"
