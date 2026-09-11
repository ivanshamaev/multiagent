# STEP-0008 — Tool and Policy Layer Evidence

Date: 2026-09-11

Status: PASS

## Verified result

The Data Engineer has a closed, versioned capability profile and typed workspace, ClickHouse, and
dbt calls. Official ClickHouse MCP 0.6.0 and dbt MCP 2.2.1 run as pinned, non-root, read-only-rootfs
stdio containers on an internal network. A local MAF facade exposes only profile tools; every MCP
call is re-authorized by a pure policy, serialized through cumulative budgets, bounded to text, and
bound to content-addressed evidence. Invalid arguments and denials abort through
`MiddlewareFailure`, rather than becoming ordinary model-visible retry results.

## Commands and outcomes

- `make mcp-images` and `make platform-up` — exit `0`; all images were recreated after deletion,
  with ClickHouse, PostgreSQL, Airflow API, scheduler, and DAG processor healthy.
- `make mcp-smoke` — exit `0`; deterministic count query returned 100000; dbt compile/test passed;
  a DDL attempt was denied before MCP execution. Evidence recorded 3 success + 1 denial and no
  denied output. The baseline build passed 76/76 resources.
- Container-local grant probe — exit `0`; `mcp_reader` returned SELECT `1`, INSERT `0`, with grants
  limited to `raw.*` and `analytics.*`.
- `make scenario-repro-test` — exit `0`; baseline `53bf4b7d…`, source `798def11…`, data
  `3823d7b5…`. `make scenario-grade-baseline-test` — exit `0`, expected `INCOMPLETE`.
- `make platform-test` — exit `0`; Airflow run
  `api_smoke_20260911T190822622109Z_1df3f8ad` passed 11/11 tasks; dbt 68/68 and independent SQL
  checks passed.
- Final `make check && git diff --check` — exit `0`; Ruff/format PASS, 210 pytest checks PASS,
  Compose valid, no whitespace errors.

## Problems and residual risks

PRB-0017 disables FastMCP update egress; PRB-0018 corrected live dbt schema drift; PRB-0019 records
the recovered host/VPN DNS outage; PRB-0020 makes scenario reproducibility fail fast. Official MCP
servers still materialize a response before the local byte cap and log policy-approved SQL text.
Tool outputs remain untrusted model context. Durable workflow checkpoints and the autonomous
workspace-edit/repair loop are intentionally deferred to STEP-0009.
