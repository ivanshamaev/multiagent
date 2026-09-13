# STEP-0014 evidence — read-only Airflow MCP

Date: 2026-09-13

Status: PASS

## Implemented boundary

- Six versioned tool contracts map only to fixed Airflow 3.3.1 `GET /api/v2` paths.
- `airflow-observer-v1` permits exactly three local DAG IDs and enforces calls, time, pagination,
  identifier, log-attempt, response-byte, and cumulative-output bounds.
- A repository FastMCP stdio process owns Viewer authentication; username/password/JWT never become
  model-visible arguments or retained evidence. DAG-run `conf` and internal execution metadata are
  removed by explicit response projection.
- The existing admin acceptance client remains separate and is not exposed to agents.

## Verification

| Command | Exit | Result |
| --- | ---: | --- |
| `make airflow-mcp-smoke` | 0 | 3 DAGs; 8 calls/evidence; acceptance run 11/11 success; metadata unchanged |
| `make check` | 0 | Ruff, format, Compose; 350 pytest checks passed |
| `make mcp-smoke` | 0 | ClickHouse SELECT and dbt compile/test passed; DDL denied |
| `make scenario-repro-test` | 0 | two resets retained matching source, baseline, and data fingerprints |
| `make scenario-grade-baseline-test` | 0 | isolated grader returned expected `INCOMPLETE` boundary result |
| `make platform-test` | 0 | Airflow/Cosmos 11/11, dbt 68/68, ClickHouse assertions PASS |
| `git diff --check` | 0 | no whitespace errors |

Live observer summary: DAG `ecommerce_acceptance`, run
`api_smoke_20260913T102947269838Z_e2f2a659`, 11 task instances, eight successful calls, eight
evidence records. Only a SHA-256 digest of the bounded log response was printed.

## Defects and residual risk

PRB-0038 fixed duplicate FastMCP text/structured output. PRB-0039 consolidated Admin/Viewer
bootstrap, bounded retry of intermittent CLI `SIGSEGV`, and credential-free failures. The built-in
Viewer permission model is accepted only for this loopback local environment. Controlled dev-DAG
trigger requires a separate future ADR, identity, profile, idempotency, and approval gate.
