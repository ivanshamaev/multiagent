"""Local stdio MCP server exposing fixed read-only Airflow API operations."""

from __future__ import annotations

import asyncio

from mcp.server.fastmcp import FastMCP

from contracts import (
    AirflowGetDagCall,
    AirflowGetDagRunCall,
    AirflowGetTaskLogCall,
    AirflowListDagRunsCall,
    AirflowListDagsCall,
    AirflowListTaskInstancesCall,
)
from runtime.tools.airflow_api import AirflowAPIAdapter, AirflowAPIConfig

mcp = FastMCP("airflow-readonly", log_level="ERROR")
_adapter: AirflowAPIAdapter | None = None


def _api() -> AirflowAPIAdapter:
    global _adapter
    if _adapter is None:
        _adapter = AirflowAPIAdapter(AirflowAPIConfig.from_env())
    return _adapter


async def _execute(call) -> str:
    return await asyncio.to_thread(_api().execute, call)


@mcp.tool(
    description="List only DAGs configured in the observer allowlist.",
    structured_output=False,
)
async def list_dags(limit: int = 50, offset: int = 0) -> str:
    return await _execute(AirflowListDagsCall(limit=limit, offset=offset))


@mcp.tool(description="Get metadata for one allowlisted DAG.", structured_output=False)
async def get_dag(dag_id: str) -> str:
    return await _execute(AirflowGetDagCall(dag_id=dag_id))


@mcp.tool(
    description="List bounded recent runs for one allowlisted DAG.",
    structured_output=False,
)
async def list_dag_runs(dag_id: str, limit: int = 20, offset: int = 0) -> str:
    return await _execute(AirflowListDagRunsCall(dag_id=dag_id, limit=limit, offset=offset))


@mcp.tool(description="Get one run for an allowlisted DAG.", structured_output=False)
async def get_dag_run(dag_id: str, dag_run_id: str) -> str:
    return await _execute(AirflowGetDagRunCall(dag_id=dag_id, dag_run_id=dag_run_id))


@mcp.tool(
    description="List bounded task instances for one allowlisted DAG run.",
    structured_output=False,
)
async def list_task_instances(
    dag_id: str,
    dag_run_id: str,
    limit: int = 100,
    offset: int = 0,
) -> str:
    return await _execute(
        AirflowListTaskInstancesCall(
            dag_id=dag_id,
            dag_run_id=dag_run_id,
            limit=limit,
            offset=offset,
        )
    )


@mcp.tool(
    description="Get one bounded task-attempt log without requesting full content.",
    structured_output=False,
)
async def get_task_log(
    dag_id: str,
    dag_run_id: str,
    task_id: str,
    try_number: int,
    map_index: int = -1,
) -> str:
    return await _execute(
        AirflowGetTaskLogCall(
            dag_id=dag_id,
            dag_run_id=dag_run_id,
            task_id=task_id,
            try_number=try_number,
            map_index=map_index,
        )
    )


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
