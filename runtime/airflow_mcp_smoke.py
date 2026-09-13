"""Live read-only smoke for the Airflow observer MCP boundary."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from hashlib import sha256

from agent_framework import FunctionTool

from policies import load_capability_profile
from runtime.scenario_harness import REPOSITORY_ROOT
from runtime.tools import connect_airflow_mcp_tools

PROFILE_PATH = REPOSITORY_ROOT / "policies/profiles/airflow_observer_v1.json"


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable {name} is missing")
    return value


def _tool(tools: tuple[FunctionTool, ...], name: str) -> FunctionTool:
    selected = tuple(item for item in tools if item.name == name)
    if len(selected) != 1:
        raise RuntimeError("Airflow MCP profile has an unexpected tool set")
    return selected[0]


async def _json(tool: FunctionTool, arguments: dict[str, object]) -> dict[str, object]:
    result = await tool.invoke(arguments=arguments)
    if not isinstance(result, (list, tuple)) or len(result) != 1:
        raise RuntimeError("Airflow MCP returned an invalid content envelope")
    text = getattr(result[0], "text", None)
    if not isinstance(text, str):
        raise RuntimeError("Airflow MCP returned non-text content")
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise RuntimeError("Airflow MCP returned a non-object response")
    return payload


def _list(payload: dict[str, object], key: str) -> list[dict[str, object]]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise RuntimeError(f"Airflow MCP response is missing {key}")
    return value


async def run_smoke(dag_id: str = "ecommerce_acceptance") -> dict[str, object]:
    profile = load_capability_profile(PROFILE_PATH)
    if dag_id not in profile.allowed_airflow_dags:
        raise RuntimeError("requested smoke DAG is absent from the observer profile")
    async with connect_airflow_mcp_tools(
        REPOSITORY_ROOT,
        profile,
        task_id="airflow-mcp-live-smoke",
        actor_id="airflow-observer-agent",
        base_url=_required("AIRFLOW_API_BASE_URL"),
        username=_required("AIRFLOW_MCP_USERNAME"),
        password=_required("AIRFLOW_MCP_PASSWORD"),
    ) as connected:
        listed = await _json(_tool(connected.tools, "airflow_list_dags"), {"limit": 50})
        before_dag = await _json(
            _tool(connected.tools, "airflow_get_dag"),
            {"dag_id": dag_id},
        )
        before_runs = await _json(
            _tool(connected.tools, "airflow_list_dag_runs"),
            {"dag_id": dag_id, "limit": 1},
        )
        runs = _list(before_runs, "dag_runs")
        if not runs or not isinstance(runs[0].get("dag_run_id"), str):
            raise RuntimeError("Airflow MCP smoke requires one completed acceptance run")
        run_id = runs[0]["dag_run_id"]
        run = await _json(
            _tool(connected.tools, "airflow_get_dag_run"),
            {"dag_id": dag_id, "dag_run_id": run_id},
        )
        instances_payload = await _json(
            _tool(connected.tools, "airflow_list_task_instances"),
            {"dag_id": dag_id, "dag_run_id": run_id, "limit": 100},
        )
        instances = _list(instances_payload, "task_instances")
        publish = next((item for item in instances if item.get("task_id") == "publish"), None)
        if publish is None or not isinstance(publish.get("try_number"), int):
            raise RuntimeError("Airflow MCP smoke could not locate the publish task attempt")
        log = await _json(
            _tool(connected.tools, "airflow_get_task_log"),
            {
                "dag_id": dag_id,
                "dag_run_id": run_id,
                "task_id": "publish",
                "try_number": publish["try_number"],
            },
        )
        after_dag = await _json(
            _tool(connected.tools, "airflow_get_dag"),
            {"dag_id": dag_id},
        )
        after_runs = await _json(
            _tool(connected.tools, "airflow_list_dag_runs"),
            {"dag_id": dag_id, "limit": 1},
        )
        evidence = connected.gateway.evidence

    dags = _list(listed, "dags")
    observed_dag_ids = {item.get("dag_id") for item in dags}
    if not observed_dag_ids.issubset(profile.allowed_airflow_dags):
        raise RuntimeError("Airflow MCP list exposed a DAG outside the observer allowlist")
    if before_dag != after_dag or before_runs != after_runs:
        raise RuntimeError("Airflow metadata changed during the read-only smoke")
    if run.get("state") != "success" or any(item.get("state") != "success" for item in instances):
        raise RuntimeError("Airflow MCP returned an unsuccessful acceptance run")
    if not log:
        raise RuntimeError("Airflow MCP returned an empty log envelope")
    return {
        "dag_count": len(dags),
        "dag_id": dag_id,
        "evidence_count": len(evidence),
        "log_response_sha256": sha256(
            json.dumps(log, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "run_id": run_id,
        "status": "PASS",
        "task_instance_count": len(instances),
        "tool_calls": connected.gateway.usage.completed_calls,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dag", default="ecommerce_acceptance")
    args = parser.parse_args(argv)
    try:
        result = asyncio.run(run_smoke(args.dag))
    except Exception as error:
        print(json.dumps({"error_type": type(error).__name__, "status": "FAIL"}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
