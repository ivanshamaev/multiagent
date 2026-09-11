from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _service(compose: str, name: str, next_name: str) -> str:
    return compose.split(f"  {name}:\n", maxsplit=1)[1].split(f"  {next_name}:\n", maxsplit=1)[0]


def test_mcp_services_are_stdio_only_hardened_and_egress_isolated() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    clickhouse = _service(compose, "clickhouse-mcp", "dbt-mcp")
    dbt = _service(compose, "dbt-mcp", "scenario-grader")

    assert "mcp-clickhouse:0.6.0@sha256:" in clickhouse
    assert 'CLICKHOUSE_ALLOW_WRITE_ACCESS: "false"' in clickhouse
    assert 'CLICKHOUSE_ALLOW_DROP: "false"' in clickhouse
    assert 'CHDB_ENABLED: "false"' in clickhouse
    assert 'CLICKHOUSE_MCP_MAX_WORKERS: "1"' in clickhouse
    assert 'CLICKHOUSE_MCP_QUERY_TIMEOUT: "15"' in clickhouse
    assert "DBT_MCP_ENABLE_TOOLS: " in dbt
    assert "parse,compile,build,test,show,list,get_lineage_dev,get_node_details_dev" in dbt
    assert "${DBT_PROJECT_PATH:-./platform/dbt}:/workspace" in dbt
    for section in (clickhouse, dbt):
        assert "ports:" not in section
        assert "env_file:" not in section
        assert "read_only: true" in section
        assert "no-new-privileges:true" in section
        assert "- ALL" in section
        assert 'FASTMCP_CHECK_FOR_UPDATES: "off"' in section
        assert 'FASTMCP_SHOW_SERVER_BANNER: "false"' in section
        assert "      - mcp" in section
        assert "      - data-platform" not in section
        assert "API_TOKEN" not in section
    networks = compose.split("networks:\n", maxsplit=1)[-1]
    assert "  mcp:\n" in networks
    assert "    internal: true" in networks


def test_dbt_mcp_image_is_hash_locked_with_exact_direct_versions() -> None:
    dockerfile = (ROOT / "mcp/dbt/Dockerfile").read_text(encoding="utf-8")
    requirements = (ROOT / "mcp/dbt/requirements.lock").read_text(encoding="utf-8")
    dockerignore = (ROOT / "mcp/dbt/.dockerignore").read_text(encoding="utf-8")

    assert "python:3.12.14-slim-bookworm@sha256:" in dockerfile
    assert "--require-hashes" in dockerfile
    assert 'ENTRYPOINT ["dbt-mcp"]' in dockerfile
    assert dockerignore.splitlines() == ["*", "!Dockerfile", "!requirements.lock"]
    for package, version in (
        ("dbt-clickhouse", "1.10.2"),
        ("dbt-core", "1.11.14"),
        ("dbt-mcp", "2.2.1"),
        ("mcp", "1.26.0"),
    ):
        assert f"{package}=={version} \\\n" in requirements


def test_clickhouse_bootstrap_resets_to_least_privilege_scopes() -> None:
    sql = (ROOT / "platform/clickhouse/security/001_mcp_users.sql").read_text(encoding="utf-8")

    assert "REVOKE ALL ON *.* FROM mcp_reader" in sql
    assert "GRANT SELECT ON raw.* TO mcp_reader" in sql
    assert "GRANT SELECT ON analytics.* TO mcp_reader" in sql
    assert "REVOKE ALL ON *.* FROM dbt_agent" in sql
    assert "GRANT SELECT ON raw.* TO dbt_agent" in sql
    assert "ON analytics.* TO dbt_agent" in sql
    assert "GRANT ALL" not in sql
    assert "API_TOKEN" not in sql
