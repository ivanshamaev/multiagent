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
)
from policies import CapabilityProfile
from runtime.tools.evidence_store import ToolEvidenceStore
from runtime.tools.mcp_gateway import MCPGatewayError, MCPToolGateway
from runtime.tools.mcp_stdio import create_clickhouse_mcp_tool, create_dbt_mcp_tool


@dataclass(frozen=True)
class ConnectedDataEngineerMCPTools:
    """Connected safe MAF facade plus inspectable usage/evidence state."""

    tools: tuple[FunctionTool, ...]
    gateway: MCPToolGateway


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
