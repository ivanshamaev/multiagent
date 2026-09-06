"""MAF stdio clients for isolated official MCP server containers."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from agent_framework import MCPStdioTool

CLICKHOUSE_MCP_TOOLS = frozenset({"list_databases", "list_tables", "run_query"})
DBT_MCP_TOOLS = frozenset(
    {
        "build",
        "compile",
        "get_lineage_dev",
        "get_node_details_dev",
        "list",
        "parse",
        "show",
        "test",
    }
)
ApprovalMode = Literal["always_require", "never_require"]


class MCPConfigurationError(RuntimeError):
    """An MCP process target crossed the repository/scenario boundary."""


def _repository_root(path: Path) -> Path:
    if path.is_symlink():
        raise MCPConfigurationError("repository root must not be a symlink")
    try:
        root = path.resolve(strict=True)
    except OSError as error:
        raise MCPConfigurationError(
            f"repository root cannot be resolved: {type(error).__name__}"
        ) from None
    if not root.is_dir() or not (root / "docker-compose.yml").is_file():
        raise MCPConfigurationError("repository root does not contain docker-compose.yml")
    return root


def _compose_stdio_args(service: str) -> list[str]:
    return [
        "compose",
        "--profile",
        "tools",
        "run",
        "--rm",
        "--no-deps",
        "-T",
        service,
    ]


def create_clickhouse_mcp_tool(
    repository_root: Path,
    *,
    approval_mode: ApprovalMode = "always_require",
) -> MCPStdioTool:
    """Create a client exposing only the three approved upstream ClickHouse tools."""

    root = _repository_root(repository_root)
    return MCPStdioTool(
        name="clickhouse-mcp",
        description="Read-only ClickHouse discovery and bounded queries",
        command="docker",
        args=_compose_stdio_args("clickhouse-mcp"),
        env={},
        cwd=str(root),
        tool_name_prefix="clickhouse",
        allowed_tools=CLICKHOUSE_MCP_TOOLS,
        load_prompts=False,
        approval_mode=approval_mode,
        request_timeout=20,
    )


def create_dbt_mcp_tool(
    repository_root: Path,
    scenario_workspace: Path,
    *,
    approval_mode: ApprovalMode = "always_require",
) -> MCPStdioTool:
    """Create a client mounting only a verified scenario's dbt project."""

    root = _repository_root(repository_root)
    if scenario_workspace.is_symlink():
        raise MCPConfigurationError("scenario workspace must not be a symlink")
    try:
        workspace = scenario_workspace.resolve(strict=True)
    except OSError as error:
        raise MCPConfigurationError(
            f"scenario workspace cannot be resolved: {type(error).__name__}"
        ) from None
    expected_parent = root / ".scenario-state/workspaces"
    if not workspace.is_dir() or not workspace.is_relative_to(expected_parent):
        raise MCPConfigurationError("dbt MCP requires a managed repository-local workspace")
    dbt_project = workspace / "platform/dbt"
    if dbt_project.is_symlink() or not (dbt_project / "dbt_project.yml").is_file():
        raise MCPConfigurationError("scenario dbt project is missing or unsafe")
    for parent in (dbt_project, *dbt_project.parents):
        if parent == root.parent:
            break
        if parent.is_symlink():
            raise MCPConfigurationError("scenario dbt path contains a symlink")

    return MCPStdioTool(
        name="dbt-mcp",
        description="dbt CLI operations in the verified disposable project",
        command="docker",
        args=_compose_stdio_args("dbt-mcp"),
        env={"DBT_PROJECT_PATH": str(dbt_project)},
        cwd=str(root),
        tool_name_prefix="dbt",
        allowed_tools=DBT_MCP_TOOLS,
        load_prompts=False,
        approval_mode=approval_mode,
        request_timeout=130,
    )
