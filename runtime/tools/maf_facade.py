"""MAF function tools that can execute only through the deterministic MCP gateway."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from hashlib import sha256
from itertools import count
from pathlib import Path

from agent_framework import FunctionTool, MiddlewareFailure, tool

from contracts import (
    AirflowGetDagCall,
    AirflowGetDagRunCall,
    AirflowGetTaskLogCall,
    AirflowListDagRunsCall,
    AirflowListDagsCall,
    AirflowListTaskInstancesCall,
    ClickHouseListDatabasesCall,
    ClickHouseListTablesCall,
    ClickHouseRunQueryCall,
    DbtBuildCall,
    DbtCompileCall,
    DbtGetLineageCall,
    DbtGetNodeDetailsCall,
    DbtListCall,
    DbtParseCall,
    DbtResourceType,
    DbtShowCall,
    DbtTestCall,
    ToolCall,
    ToolName,
    ToolRequest,
    WorkspaceReadCall,
    WorkspaceWriteCall,
)
from policies import CapabilityProfile
from runtime.scenario_harness import ScenarioManifest
from runtime.tools.evidence_store import ToolEvidenceStore
from runtime.tools.mcp_gateway import MCPGatewayError, MCPToolGateway
from runtime.tools.mcp_stdio import (
    create_airflow_mcp_tool,
    create_clickhouse_mcp_tool,
    create_dbt_mcp_tool,
)
from runtime.tools.workspace import WorkspaceToolAdapter


@dataclass(frozen=True)
class ConnectedDataEngineerMCPTools:
    """Connected safe MAF facade plus inspectable usage/evidence state."""

    tools: tuple[FunctionTool, ...]
    gateway: MCPToolGateway


@dataclass(frozen=True)
class ConnectedAirflowMCPTools:
    tools: tuple[FunctionTool, ...]
    gateway: MCPToolGateway


class AirflowMCPTools:
    """Bind observer identity to the six closed Airflow schemas."""

    def __init__(
        self,
        gateway: MCPToolGateway,
        *,
        task_id: str,
        actor_id: str,
        role: str = "airflow-observer",
    ) -> None:
        self._gateway = gateway
        self._task_id = task_id
        self._actor_id = actor_id
        self._role = role
        self._sequence = count(1)
        self.tools = tuple(
            function
            for canonical, function in self._build_candidates()
            if canonical in gateway.allowed_tools
        )

    async def _execute(self, call: ToolCall) -> str:
        sequence = next(self._sequence)
        seed = f"{self._task_id}:{self._actor_id}:{sequence}"
        request = ToolRequest(
            request_id=f"tool-request-{sha256(seed.encode()).hexdigest()[:24]}",
            task_id=self._task_id,
            actor_id=self._actor_id,
            role=self._role,
            call=call,
        )
        try:
            return (await self._gateway.execute(request)).content
        except MCPGatewayError as error:
            raise MiddlewareFailure(str(error)) from error

    async def _validated(self, factory: Callable[..., ToolCall], **arguments: object) -> str:
        try:
            call = factory(**arguments)
        except (TypeError, ValueError) as error:
            raise MiddlewareFailure("tool arguments failed closed validation") from error
        return await self._execute(call)

    def _build_candidates(self) -> tuple[tuple[ToolName, FunctionTool], ...]:
        @tool(
            name="airflow_list_dags",
            description="List allowlisted DAG metadata only.",
            approval_mode="never_require",
        )
        async def list_dags(limit: int = 50, offset: int = 0) -> str:
            return await self._validated(AirflowListDagsCall, limit=limit, offset=offset)

        @tool(
            name="airflow_get_dag",
            description="Get one allowlisted DAG.",
            approval_mode="never_require",
        )
        async def get_dag(dag_id: str) -> str:
            return await self._validated(AirflowGetDagCall, dag_id=dag_id)

        @tool(
            name="airflow_list_dag_runs",
            description="List bounded runs for one DAG.",
            approval_mode="never_require",
        )
        async def list_dag_runs(dag_id: str, limit: int = 20, offset: int = 0) -> str:
            return await self._validated(
                AirflowListDagRunsCall,
                dag_id=dag_id,
                limit=limit,
                offset=offset,
            )

        @tool(
            name="airflow_get_dag_run",
            description="Get one DAG run.",
            approval_mode="never_require",
        )
        async def get_dag_run(dag_id: str, dag_run_id: str) -> str:
            return await self._validated(
                AirflowGetDagRunCall,
                dag_id=dag_id,
                dag_run_id=dag_run_id,
            )

        @tool(
            name="airflow_list_task_instances",
            description="List bounded task instances for one DAG run.",
            approval_mode="never_require",
        )
        async def list_task_instances(
            dag_id: str,
            dag_run_id: str,
            limit: int = 100,
            offset: int = 0,
        ) -> str:
            return await self._validated(
                AirflowListTaskInstancesCall,
                dag_id=dag_id,
                dag_run_id=dag_run_id,
                limit=limit,
                offset=offset,
            )

        @tool(
            name="airflow_get_task_log",
            description="Get one bounded task-attempt log.",
            approval_mode="never_require",
        )
        async def get_task_log(
            dag_id: str,
            dag_run_id: str,
            task_id: str,
            try_number: int,
            map_index: int = -1,
        ) -> str:
            return await self._validated(
                AirflowGetTaskLogCall,
                dag_id=dag_id,
                dag_run_id=dag_run_id,
                task_id=task_id,
                try_number=try_number,
                map_index=map_index,
            )

        return (
            (ToolName.AIRFLOW_LIST_DAGS, list_dags),
            (ToolName.AIRFLOW_GET_DAG, get_dag),
            (ToolName.AIRFLOW_LIST_DAG_RUNS, list_dag_runs),
            (ToolName.AIRFLOW_GET_DAG_RUN, get_dag_run),
            (ToolName.AIRFLOW_LIST_TASK_INSTANCES, list_task_instances),
            (ToolName.AIRFLOW_GET_TASK_LOG, get_task_log),
        )


class DataEngineerMCPTools:
    """Bind workflow-owned identity to closed MAF schemas and one MCP gateway."""

    def __init__(
        self,
        gateway: MCPToolGateway,
        *,
        task_id: str,
        actor_id: str,
        role: str = "data-engineer",
    ) -> None:
        self._gateway = gateway
        self._task_id = task_id
        self._actor_id = actor_id
        self._role = role
        self._sequence = count(1)
        candidates = self._build_candidates()
        self.tools = tuple(
            function
            for canonical_name, function in candidates
            if canonical_name in gateway.allowed_tools
        )

    async def _execute(self, call: ToolCall) -> str:
        sequence = next(self._sequence)
        seed = f"{self._task_id}:{self._actor_id}:{sequence}"
        request = ToolRequest(
            request_id=f"tool-request-{sha256(seed.encode()).hexdigest()[:24]}",
            task_id=self._task_id,
            actor_id=self._actor_id,
            role=self._role,
            call=call,
        )
        try:
            result = await self._gateway.execute(request)
        except MCPGatewayError as error:
            raise MiddlewareFailure(str(error)) from error
        return result.content

    async def _validated(
        self,
        factory: Callable[..., ToolCall],
        **arguments: object,
    ) -> str:
        try:
            call = factory(**arguments)
        except (TypeError, ValueError) as error:
            raise MiddlewareFailure("tool arguments failed closed validation") from error
        return await self._execute(call)

    def _build_candidates(self) -> tuple[tuple[ToolName, FunctionTool], ...]:
        @tool(
            name="workspace_read_file",
            description="Read one bounded UTF-8 file from the verified scenario workspace.",
            approval_mode="never_require",
        )
        async def workspace_read_file(path: str) -> str:
            return await self._validated(WorkspaceReadCall, path=path)

        @tool(
            name="workspace_write_file",
            description="Atomically write one allowed file in the verified scenario workspace.",
            approval_mode="never_require",
        )
        async def workspace_write_file(path: str, content: str) -> str:
            return await self._validated(WorkspaceWriteCall, path=path, content=content)

        @tool(
            name="clickhouse_list_databases",
            description="List ClickHouse databases through the read-only policy gateway.",
            approval_mode="never_require",
        )
        async def clickhouse_list_databases() -> str:
            return await self._validated(ClickHouseListDatabasesCall)

        @tool(
            name="clickhouse_list_tables",
            description="List bounded table metadata in one allowed ClickHouse database.",
            approval_mode="never_require",
        )
        async def clickhouse_list_tables(
            database: str,
            page_size: int = 50,
            include_detailed_columns: bool = False,
            like: str | None = None,
            not_like: str | None = None,
            page_token: str | None = None,
        ) -> str:
            return await self._validated(
                ClickHouseListTablesCall,
                database=database,
                page_size=page_size,
                include_detailed_columns=include_detailed_columns,
                like=like,
                not_like=not_like,
                page_token=page_token,
            )

        @tool(
            name="clickhouse_run_query",
            description="Run one read-only ClickHouse query with a literal bounded LIMIT.",
            approval_mode="never_require",
        )
        async def clickhouse_run_query(query: str) -> str:
            return await self._validated(ClickHouseRunQueryCall, query=query)

        @tool(
            name="dbt_parse",
            description="Parse the verified disposable dbt project.",
            approval_mode="never_require",
        )
        async def dbt_parse() -> str:
            return await self._validated(DbtParseCall)

        @tool(
            name="dbt_compile",
            description="Compile an optional safe dbt node selection.",
            approval_mode="never_require",
        )
        async def dbt_compile(
            node_selection: str | None = None,
            yml_selector: str | None = None,
        ) -> str:
            return await self._validated(
                DbtCompileCall,
                node_selection=node_selection,
                yml_selector=yml_selector,
            )

        @tool(
            name="dbt_build",
            description="Build and test an optional safe dbt node selection.",
            approval_mode="never_require",
        )
        async def dbt_build(
            node_selection: str | None = None,
            yml_selector: str | None = None,
        ) -> str:
            return await self._validated(
                DbtBuildCall,
                node_selection=node_selection,
                yml_selector=yml_selector,
            )

        @tool(
            name="dbt_test",
            description="Test an optional safe dbt node selection.",
            approval_mode="never_require",
        )
        async def dbt_test(
            node_selection: str | None = None,
            yml_selector: str | None = None,
        ) -> str:
            return await self._validated(
                DbtTestCall,
                node_selection=node_selection,
                yml_selector=yml_selector,
            )

        @tool(
            name="dbt_show",
            description="Preview an allowed read query with a separate bounded row limit.",
            approval_mode="never_require",
        )
        async def dbt_show(sql_query: str, limit: int = 5) -> str:
            return await self._validated(DbtShowCall, sql_query=sql_query, limit=limit)

        @tool(
            name="dbt_list",
            description="List selected dbt resources using a bounded resource-type allowlist.",
            approval_mode="never_require",
        )
        async def dbt_list(
            node_selection: str | None = None,
            yml_selector: str | None = None,
            resource_type: list[DbtResourceType] | None = None,
        ) -> str:
            return await self._validated(
                DbtListCall,
                node_selection=node_selection,
                yml_selector=yml_selector,
                resource_type=() if resource_type is None else tuple(resource_type),
            )

        @tool(
            name="dbt_get_lineage_dev",
            description="Get bounded-depth lineage for one dbt unique ID.",
            approval_mode="never_require",
        )
        async def dbt_get_lineage_dev(unique_id: str, depth: int = 1) -> str:
            return await self._validated(
                DbtGetLineageCall,
                unique_id=unique_id,
                depth=depth,
            )

        @tool(
            name="dbt_get_node_details_dev",
            description="Get details for one dbt node ID.",
            approval_mode="never_require",
        )
        async def dbt_get_node_details_dev(node_id: str) -> str:
            return await self._validated(DbtGetNodeDetailsCall, node_id=node_id)

        return (
            (ToolName.WORKSPACE_READ_FILE, workspace_read_file),
            (ToolName.WORKSPACE_WRITE_FILE, workspace_write_file),
            (ToolName.CLICKHOUSE_LIST_DATABASES, clickhouse_list_databases),
            (ToolName.CLICKHOUSE_LIST_TABLES, clickhouse_list_tables),
            (ToolName.CLICKHOUSE_RUN_QUERY, clickhouse_run_query),
            (ToolName.DBT_PARSE, dbt_parse),
            (ToolName.DBT_COMPILE, dbt_compile),
            (ToolName.DBT_BUILD, dbt_build),
            (ToolName.DBT_TEST, dbt_test),
            (ToolName.DBT_SHOW, dbt_show),
            (ToolName.DBT_LIST, dbt_list),
            (ToolName.DBT_GET_LINEAGE_DEV, dbt_get_lineage_dev),
            (ToolName.DBT_GET_NODE_DETAILS_DEV, dbt_get_node_details_dev),
        )


@asynccontextmanager
async def connect_data_engineer_mcp_tools(
    repository_root: Path,
    scenario_workspace: Path,
    profile: CapabilityProfile,
    *,
    task_id: str,
    actor_id: str,
    role: str = "data-engineer",
) -> AsyncIterator[ConnectedDataEngineerMCPTools]:
    """Connect isolated servers while exposing only policy-enforcing local tools."""

    clickhouse = create_clickhouse_mcp_tool(repository_root)
    dbt = create_dbt_mcp_tool(repository_root, scenario_workspace)
    store = ToolEvidenceStore(repository_root, repository_root / ".scenario-state")
    async with clickhouse, dbt:
        gateway = MCPToolGateway(profile, clickhouse, dbt, store)
        facade = DataEngineerMCPTools(
            gateway,
            task_id=task_id,
            actor_id=actor_id,
            role=role,
        )
        yield ConnectedDataEngineerMCPTools(tools=facade.tools, gateway=gateway)


@asynccontextmanager
async def connect_data_engineer_tools(
    repository_root: Path,
    scenario_workspace: Path,
    manifest: ScenarioManifest,
    profile: CapabilityProfile,
    *,
    task_id: str,
    actor_id: str,
    role: str = "data-engineer",
) -> AsyncIterator[ConnectedDataEngineerMCPTools]:
    """Connect one unified workspace/MCP facade with cumulative task budgets."""

    clickhouse = create_clickhouse_mcp_tool(repository_root)
    dbt = create_dbt_mcp_tool(repository_root, scenario_workspace)
    store = ToolEvidenceStore(repository_root, repository_root / ".scenario-state")
    workspace = WorkspaceToolAdapter(repository_root, manifest, profile)
    async with clickhouse, dbt:
        gateway = MCPToolGateway(profile, clickhouse, dbt, store, workspace)
        facade = DataEngineerMCPTools(
            gateway,
            task_id=task_id,
            actor_id=actor_id,
            role=role,
        )
        yield ConnectedDataEngineerMCPTools(tools=facade.tools, gateway=gateway)


@asynccontextmanager
async def connect_airflow_mcp_tools(
    repository_root: Path,
    profile: CapabilityProfile,
    *,
    task_id: str,
    actor_id: str,
    base_url: str,
    username: str,
    password: str,
    role: str = "airflow-observer",
) -> AsyncIterator[ConnectedAirflowMCPTools]:
    """Connect only the repository-owned Airflow observer MCP process."""

    airflow = create_airflow_mcp_tool(
        repository_root,
        base_url=base_url,
        username=username,
        password=password,
        allowed_dags=profile.allowed_airflow_dags,
    )
    store = ToolEvidenceStore(repository_root, repository_root / ".scenario-state")
    async with airflow:
        gateway = MCPToolGateway(profile, None, None, store, airflow=airflow)
        facade = AirflowMCPTools(
            gateway,
            task_id=task_id,
            actor_id=actor_id,
            role=role,
        )
        yield ConnectedAirflowMCPTools(tools=facade.tools, gateway=gateway)
