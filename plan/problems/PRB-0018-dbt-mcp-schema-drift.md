# PRB-0018 — dbt MCP argument schema drift

Status: closed
Detected: 2026-09-11
Resolved: 2026-09-11

## Symptom and reproduction

The initial local contracts represented `dbt list.resource_type` as one string,
`get_lineage_dev` with separate upstream/downstream depths, and required an inline SQL `LIMIT` for
`dbt show`. After rebuilding the deleted tool containers, a live MAF `functions` inspection against
the pinned `dbt-mcp==2.2.1` image showed different server schemas: resource types are a list,
lineage has one `depth`, and show applies its own separate `limit` argument.

## Root cause

The contracts were drafted from conceptual tool behavior before the exact pinned server schemas
were inspected. This was contract drift, not a dbt runtime failure.

## Accepted fix

The typed calls now match a deliberately narrower subset of the live schemas. `dbt list` accepts a
unique bounded tuple of approved types; lineage accepts one bounded depth; `dbt show` rejects an
inline SQL limit and requires the separately validated row limit. dbt selectors are now explicitly
mutually exclusive. The MCP gateway serializes only these validated fields, so additional upstream
arguments such as vars or full-refresh cannot pass through.

## Regression check and follow-up

`tests/unit/test_tool_contracts.py`, `tests/policy/test_tool_policy.py`, and
`tests/unit/test_mcp_gateway.py` cover the corrected shapes and gateway serialization. Whenever an
MCP version changes, inspect its live advertised schemas before changing either the pin or local
contracts.
