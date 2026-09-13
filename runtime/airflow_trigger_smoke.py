"""Live approved/idempotent trigger smoke using the dedicated Airflow identity."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import UTC, datetime

from contracts import (
    AirflowGetDagRunCall,
    AirflowListTaskInstancesCall,
    AirflowTriggerDagCall,
    ToolRequest,
)
from policies import load_capability_profile
from runtime.scenario_harness import REPOSITORY_ROOT
from runtime.tools import (
    AirflowAPIAdapter,
    AirflowAPIConfig,
    AirflowApprovalStore,
    connect_airflow_trigger_tools,
)

PROFILE = REPOSITORY_ROOT / "policies/profiles/airflow_trigger_v1.json"
TASK_ID = "airflow-controlled-trigger-smoke"
DAG_ID = "ecommerce_acceptance"


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable {name} is missing")
    return value


async def _trigger(approval_id: str, key: str, connected, sequence: int) -> dict[str, object]:
    request = {
        "request_id": f"airflow-trigger-smoke-{sequence}",
        "task_id": TASK_ID,
        "actor_id": "airflow-trigger-controller",
        "role": "airflow-trigger-controller",
        "call": AirflowTriggerDagCall(
            task_id=TASK_ID,
            dag_id=DAG_ID,
            idempotency_key=key,
            approval_id=approval_id,
        ),
    }
    result = await connected.gateway.execute(ToolRequest(**request))
    payload = json.loads(result.content)
    if not isinstance(payload, dict):
        raise RuntimeError("trigger MCP returned a non-object response")
    return payload


async def run_smoke() -> dict[str, object]:
    profile = load_capability_profile(PROFILE)
    key = f"smoke-{datetime.now(UTC).strftime('%Y%m%dT%H%M%S%f')}"
    approvals = AirflowApprovalStore(REPOSITORY_ROOT)
    first_approval = approvals.create(
        task_id=TASK_ID,
        dag_id=DAG_ID,
        idempotency_key=key,
        approved_by="integration-gate",
    )
    async with connect_airflow_trigger_tools(
        REPOSITORY_ROOT,
        profile,
        task_id=TASK_ID,
        actor_id="airflow-trigger-controller",
        base_url=_required("AIRFLOW_API_BASE_URL"),
        username=_required("AIRFLOW_TRIGGER_USERNAME"),
        password=_required("AIRFLOW_TRIGGER_PASSWORD"),
    ) as connected:
        first = await _trigger(first_approval.approval_id, key, connected, 1)
        second_approval = approvals.create(
            task_id=TASK_ID,
            dag_id=DAG_ID,
            idempotency_key=key,
            approved_by="integration-gate",
        )
        second = await _trigger(second_approval.approval_id, key, connected, 2)
        evidence = connected.gateway.evidence

    run_id = first.get("dag_run_id")
    if (
        not isinstance(run_id, str)
        or second.get("dag_run_id") != run_id
        or first.get("trigger_outcome") != "created"
        or second.get("trigger_outcome") != "existing"
    ):
        raise RuntimeError("trigger idempotency outcome is invalid")

    observer = AirflowAPIAdapter(
        AirflowAPIConfig(
            base_url=_required("AIRFLOW_API_BASE_URL"),
            username=_required("AIRFLOW_MCP_USERNAME"),
            password=_required("AIRFLOW_MCP_PASSWORD"),
            allowed_dags=frozenset({DAG_ID}),
        )
    )
    timeout = float(os.environ.get("AIRFLOW_API_POLL_TIMEOUT_SECONDS", "300"))
    deadline = asyncio.get_running_loop().time() + timeout
    while True:
        run = json.loads(
            await asyncio.to_thread(
                observer.execute,
                AirflowGetDagRunCall(dag_id=DAG_ID, dag_run_id=run_id),
            )
        )
        if run.get("state") in {"success", "failed"}:
            break
        if asyncio.get_running_loop().time() >= deadline:
            raise RuntimeError("triggered DAG run did not finish within the poll budget")
        await asyncio.sleep(2)
    tasks_payload = json.loads(
        await asyncio.to_thread(
            observer.execute,
            AirflowListTaskInstancesCall(dag_id=DAG_ID, dag_run_id=run_id),
        )
    )
    tasks = tasks_payload.get("task_instances")
    if run.get("state") != "success" or not isinstance(tasks, list):
        raise RuntimeError("controlled trigger did not produce a successful DAG run")
    if len(tasks) != 11 or any(item.get("state") != "success" for item in tasks):
        raise RuntimeError("controlled trigger task graph is incomplete")
    return {
        "dag_id": DAG_ID,
        "evidence_count": len(evidence),
        "idempotency": "created_then_existing",
        "run_id": run_id,
        "status": "PASS",
        "task_instance_count": len(tasks),
        "trigger_calls": 2,
    }


def main() -> int:
    try:
        result = asyncio.run(run_smoke())
    except Exception as error:
        print(json.dumps({"error_type": type(error).__name__, "status": "FAIL"}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
