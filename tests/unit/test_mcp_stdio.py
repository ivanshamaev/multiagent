from pathlib import Path

import pytest

from runtime.tools import (
    AIRFLOW_TRIGGER_MCP_TOOLS,
    CLICKHOUSE_MCP_TOOLS,
    DBT_MCP_TOOLS,
    MCPConfigurationError,
    create_airflow_trigger_mcp_tool,
    create_clickhouse_mcp_tool,
    create_dbt_mcp_tool,
)


def test_airflow_trigger_mcp_is_separate_and_always_requires_approval(tmp_path: Path) -> None:
    root, _ = _repository(tmp_path)

    tool = create_airflow_trigger_mcp_tool(
        root,
        base_url="http://127.0.0.1:8080",
        username="trigger-user",
        password="trigger-password",
        allowed_dag="ecommerce_acceptance",
    )

    assert tool.allowed_tools == AIRFLOW_TRIGGER_MCP_TOOLS
    assert tool.approval_mode == "always_require"
    assert tool.args == ["-m", "runtime.airflow_trigger_mcp_server"]
    assert tool.env["AIRFLOW_TRIGGER_ALLOWED_DAG"] == "ecommerce_acceptance"
    assert "AIRFLOW_MCP_USERNAME" not in tool.env


def _repository(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "repository"
    root.mkdir()
    (root / "docker-compose.yml").write_text("services: {}\n", encoding="utf-8")
    workspace = root / ".scenario-state/workspaces/example"
    project = workspace / "platform/dbt"
    project.mkdir(parents=True)
    (project / "dbt_project.yml").write_text("name: example\n", encoding="utf-8")
    return root, workspace


def test_clickhouse_mcp_client_is_fixed_stdio_and_fail_closed_by_default(tmp_path: Path) -> None:
    root, _ = _repository(tmp_path)

    tool = create_clickhouse_mcp_tool(root)

    assert tool.command == "docker"
    assert tool.args == [
        "compose",
        "--profile",
        "tools",
        "run",
        "--rm",
        "--no-deps",
        "-T",
        "clickhouse-mcp",
    ]
    assert tool.env == {}
    assert tool.allowed_tools == CLICKHOUSE_MCP_TOOLS
    assert tool.approval_mode == "always_require"
    assert tool.tool_name_prefix == "clickhouse"
    assert tool._client_kwargs == {"cwd": str(root)}


def test_dbt_mcp_client_passes_only_verified_project_path(tmp_path: Path) -> None:
    root, workspace = _repository(tmp_path)

    tool = create_dbt_mcp_tool(root, workspace)

    assert tool.allowed_tools == DBT_MCP_TOOLS
    assert tool.approval_mode == "always_require"
    assert tool.env == {"DBT_PROJECT_PATH": str(workspace / "platform/dbt")}
    serialized = repr((tool.args, tool.env, tool._client_kwargs))
    assert "API_TOKEN" not in serialized
    assert "PASSWORD" not in serialized
    assert ".env" not in serialized


def test_dbt_mcp_rejects_checkout_and_outside_workspaces(tmp_path: Path) -> None:
    root, _ = _repository(tmp_path)
    checkout_project = root / "platform/dbt"
    checkout_project.mkdir(parents=True)
    (checkout_project / "dbt_project.yml").write_text("name: checkout\n", encoding="utf-8")
    outside = tmp_path / "outside"
    (outside / "platform/dbt").mkdir(parents=True)
    (outside / "platform/dbt/dbt_project.yml").write_text("name: outside\n", encoding="utf-8")

    with pytest.raises(MCPConfigurationError, match="managed"):
        create_dbt_mcp_tool(root, root)
    with pytest.raises(MCPConfigurationError, match="managed"):
        create_dbt_mcp_tool(root, outside)


def test_mcp_repository_or_workspace_symlinks_are_rejected(tmp_path: Path) -> None:
    root, workspace = _repository(tmp_path)
    root_link = tmp_path / "repository-link"
    root_link.symlink_to(root, target_is_directory=True)
    workspace_link = root / ".scenario-state/workspaces/example-link"
    workspace_link.symlink_to(workspace, target_is_directory=True)

    with pytest.raises(MCPConfigurationError, match="symlink"):
        create_clickhouse_mcp_tool(root_link)
    with pytest.raises(MCPConfigurationError, match="symlink"):
        create_dbt_mcp_tool(root, workspace_link)
