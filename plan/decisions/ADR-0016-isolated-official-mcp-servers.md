# ADR-0016 — Isolated official MCP servers behind local policy

Status: accepted

Date: 2026-09-06

## Context

The proposal requires official ClickHouse and dbt MCP servers, but neither server is itself the
authorization boundary. `mcp-clickhouse` documents that its query guard is defense in depth and
that the ClickHouse user's grants are the security boundary. `dbt-mcp` exposes modifying CLI tools
and enables broad toolsets by default unless its explicit enable mode is used. Both projects and
MAF changed materially since the initial design document.

The control-plane `.venv` already has pinned MAF/OpenAI dependencies. Installing two server stacks
there would couple FastMCP, dbt, adapters and API clients to the orchestrator. Remote HTTP adds an
unneeded listener and authentication surface for a single-host development runtime.

## Decision

Use official `mcp-clickhouse==0.6.0` and `dbt-mcp==2.2.1` as separate pinned processes. Run them via
stdio with MAF `MCPStdioTool`; do not expose MCP HTTP ports. Pin MCP client support in the local
runtime to `mcp==1.26.0`, matching dbt-mcp's exact SDK dependency. Server dependencies remain
outside the control-plane environment, preferably in purpose-built Docker images on the existing
Compose network. Images, packages and transitive locks must be reproducible before the live gate.

ClickHouse MCP receives only a dedicated database credential with server-side read-only grants,
`CLICKHOUSE_ALLOW_WRITE_ACCESS=false`, `CLICKHOUSE_ALLOW_DROP=false`, a bounded query timeout and
one worker. Only `list_databases`, `list_tables` and `run_query` are exposed. chDB is disabled.

dbt MCP receives only `DBT_PROJECT_DIR` for the verified disposable scenario and its fixed dbt
executable. Use enable mode with exact tool names; no dbt Platform/API tokens, SQL toolset, codegen,
LSP, docs/network tools or arbitrary executable path is exposed. The first profile allows
`parse`, `compile`, `build`, `test`, `show`, `list`, `get_lineage_dev` and
`get_node_details_dev`; role policy may narrow this further.

MAF's `allowed_tools` is defense in depth. A repository-owned pure policy checks role, tool,
normalized arguments, paths and budgets before execution. Provider/runtime kwargs never carry
credentials into MCP arguments. Server sampling remains denied. Tool output is untrusted and
becomes bounded, hashed evidence before reuse.

## Alternatives

- Install both servers in `.venv` — rejected because server dependencies and dbt adapters would
  enlarge and destabilize the control plane.
- Use Streamable HTTP — deferred because local stdio has no listener/auth configuration and owns a
  simpler process lifetime.
- Implement replacement ClickHouse/dbt MCP servers — rejected; wrappers may enforce policy but do
  not duplicate official protocol/tool implementations.
- Trust only server-side tool lists — rejected because tool discovery and server configuration can
  drift, and neither validates our role/workspace/budget contract.

## Consequences and validation

There are multiple intentional gates: role policy, MAF tool allowlist, MCP server flags/tool
enable-list, filesystem mounts and database grants. Startup is slower than an in-process client,
but dependency and credential boundaries are inspectable. Unit tests use fake executors; live MCP
processes start only through explicit Make targets after resolved Compose and secret scans.

Sources: official ClickHouse [README](https://github.com/ClickHouse/mcp-clickhouse), dbt
[self-hosted setup](https://docs.getdbt.com/docs/dbt-ai/setup-local-mcp), dbt
[tool catalog](https://github.com/dbt-labs/dbt-mcp#tools), and MAF
[MCP guide](https://learn.microsoft.com/en-us/agent-framework/user-guide/model-context-protocol/using-mcp-tools).
