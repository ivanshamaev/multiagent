# STEP-0015 evidence — controlled dev-DAG trigger

Date: 2026-09-13

Status: PASS

## Implemented boundary

- A standalone trigger MCP/profile uses dedicated `airflow_trigger` credentials and permits only
  `ecommerce_acceptance`; the observer remains GET-only.
- The adapter derives `approved__<sha256>` from DAG plus bounded idempotency key, reconciles before
  and after POST, and sends only `dag_run_id`, `logical_date: null`, and empty `conf`.
- Mode-0600, locked, atomic approval records bind task, DAG, key, approver and expiry, then become
  terminal after one consumption. MAF marks the function `always_require`.
- The exact FAB role contains DAG-run create/read, acceptance-DAG edit/read, and FAB-required
  Website read. It has no broad DAG, admin, metadata-DB, pause, retry, or arbitrary API tool.

## Verification

| Command | Exit | Result |
| --- | ---: | --- |
| `make airflow-trigger-smoke` | 0 | created then existing; same run; 2 evidence; 11/11 tasks success |
| `make check` | 0 | Ruff, format, Compose; 371 pytest checks passed |
| `make airflow-mcp-smoke` | 0 | observer regression: 8 calls/evidence; 11/11 success |
| `make mcp-smoke` | 0 | ClickHouse SELECT and dbt compile/test passed; DDL denied |
| `make scenario-repro-test` | 0 | two resets retained matching fingerprints |
| `make scenario-grade-baseline-test` | 0 | expected isolated `INCOMPLETE` result |
| `make platform-test` | 0 | Airflow/Cosmos, dbt 68/68 and SQL assertions PASS |
| `git diff --check` | 0 | no whitespace errors |

Live trigger run `approved__f59c8f40faccd36a648286bec9552b9f` was created once and returned by
the same-key retry. The fixture restored the DAG to paused. No LLM call or production credential
was used. PRB-0040 and PRB-0041 retain the two integration defects and fixes.
