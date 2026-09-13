"""Separate stdio MCP server for one approved local Airflow trigger."""

from __future__ import annotations

import asyncio

from mcp.server.fastmcp import FastMCP

from contracts import AirflowTriggerDagCall
from runtime.tools.airflow_trigger import AirflowTriggerAdapter, AirflowTriggerConfig

mcp = FastMCP("airflow-controlled-trigger", log_level="ERROR")
_adapter: AirflowTriggerAdapter | None = None


def _api() -> AirflowTriggerAdapter:
    global _adapter
    if _adapter is None:
        _adapter = AirflowTriggerAdapter(AirflowTriggerConfig.from_env())
    return _adapter


@mcp.tool(
    description="Trigger the one approved local DAG with code-owned idempotency.",
    structured_output=False,
)
async def trigger_dag(
    task_id: str,
    dag_id: str,
    idempotency_key: str,
    approval_id: str,
) -> str:
    call = AirflowTriggerDagCall(
        task_id=task_id,
        dag_id=dag_id,
        idempotency_key=idempotency_key,
        approval_id=approval_id,
    )
    return await asyncio.to_thread(_api().execute, call)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
