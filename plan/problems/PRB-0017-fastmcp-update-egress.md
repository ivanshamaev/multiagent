# PRB-0017 — Upstream MCP banner attempted update-check egress

Status: closed

Date: 2026-09-06

## Symptom and reproduction

The first `MCPStdioTool` handshake with pinned `mcp-clickhouse==0.6.0` advertised only the expected
three tools, but stderr recorded an HTTP GET to the FastMCP package endpoint on PyPI. No task or
credential data was sent, yet the connection proved the container had unnecessary internet egress.

## Root cause

FastMCP 4.0.0 displays a startup banner and performs a best-effort update check by default. The MCP
container was attached to the ordinary `data-platform` bridge, which permits outbound traffic.

## Accepted fix

Set `FASTMCP_CHECK_FOR_UPDATES=off` and `FASTMCP_SHOW_SERVER_BANNER=false`. Attach both MCP services
and ClickHouse to a dedicated Docker `mcp` network marked `internal: true`; MCP containers no longer
join the internet-capable `data-platform` network. stdio remains the only MCP transport.

## Regression check and follow-up

Repeat the handshake and assert the exact advertised tool sets with no HTTP/update log. Compose
policy tests require the update flags, internal network, absent ports/env-file and isolated mounts.
Container networking is defense in depth; future MCP services must explicitly justify any egress.
