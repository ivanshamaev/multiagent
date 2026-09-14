# Isolated MCP processes

The control plane starts both official servers over stdio; neither service publishes an MCP port.

- ClickHouse uses the upstream `ghcr.io/clickhouse/mcp-clickhouse:0.6.0` multi-arch image pinned by
  digest. Server write/drop flags are false and the `mcp_reader` database user has SELECT-only
  grants.
- dbt uses `dbt-mcp==2.2.1` in a separately locked image with dbt Core 1.11.14 and
  dbt-clickhouse 1.10.2. Only the verified scenario dbt directory is mounted. Exact enabled tools
  are configured in Compose; remote, docs, SQL-generation, codegen, LSP and MCP Apps are absent.

Run `make mcp-images` to resolve/build images and `make mcp-users` to recreate least-privilege
grants. Runtime clients use `docker compose run --rm --no-deps -T <service>` as their stdio command.
Never pass `API_TOKEN` or the host `.env` to these containers.

Role-facing MAF tools authenticate every canonical `ToolRequest` before it reaches the policy
gateway. The local bearer is HS256-signed, short-lived and bound to runner/profile/role/actor/task,
audience and request hash. The owner-only signing key is not forwarded to stdio MCP servers. This
local mechanism is not the future HTTP protocol: remote MCP must use OAuth 2.1 resource/audience
validation and must not pass its access token to downstream Data Platform APIs.
