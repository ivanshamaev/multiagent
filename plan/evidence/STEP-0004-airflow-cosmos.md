# Evidence — STEP-0004 Airflow + Cosmos dbt execution

Captured: 2026-09-05, 17:45–18:09 UTC.

## Configuration fingerprint

Base commit: `176ac0b994299dcf99ae77bb579b56efd30453da`, with the STEP-0004 working tree. Runtime source checksum: `4c2cebe9f9761dfef2b7367dd338bb9c5cd1c7d39f634ab20790b90f2ac76f39`; exact scope is in the [transcript](STEP-0004-fresh-transcript.md).

- Airflow image ID: `sha256:95c7be7e969d2a414d3a43679b779c32443b86ed7f3bc0a597888f64da6772bd`.
- Versions: Airflow 3.3.1, Astronomer Cosmos 1.15.0, dbt Core 1.11.14, dbt-clickhouse 1.10.2.
- Cosmos mode: LOCAL + isolated SUBPROCESS executable; `DbtTaskGroup`; `TestBehavior.AFTER_ALL`; dbt project read-only.

## Acceptance results

All supported gate commands returned exit code `0`.

| Gate | Observed result |
| --- | --- |
| `make airflow-version` | both Python environments pass `pip check`; all pinned versions match |
| `make seed` | deterministic raw and analytics reset completed |
| `make dbt-build` | 8 models + 68 tests; PASS=76, WARN=0, ERROR=0 |
| `make airflow-test` twice | two independent 11/11 Cosmos runs and SQL baseline PASS |
| `make airflow-failure-test` | expected failed dbt test; `publish=upstream_failed`; SQL baseline unchanged |
| `make platform-test` | third 11/11 Cosmos run; raw SQL, 68 dbt tests and mart SQL PASS |
| `make check`; `git diff --check` | Ruff, 32 pytest tests, Compose and whitespace PASS |
| resolved config + container checks | `API_TOKEN`, `env_file` and Docker socket absent |

Positive run IDs and observed Airflow intervals:

- `api_smoke_20260905T175731036564Z_453330f4`, success, 17:57:31–17:58:21 UTC.
- `api_smoke_20260905T180008738709Z_00823606`, success, 18:00:09–18:00:51 UTC.
- `api_smoke_20260905T180138301267Z_a3908eb5`, success, 18:01:38–18:02:20 UTC.

Negative run: `api_smoke_20260905T175905584317Z_23ea7e57`, failed as expected; `load_raw=success`, `dbt_tests=failed`, `publish=upstream_failed`.

## Meaning and limits

Phase A now proves real dbt construction and tests inside Airflow, not marker execution. `ecommerce_hourly` remains paused by default; acceptance uses a manual schedule-free twin built by the same factory. No GateLLM call was made. Cosmos 1.15.0 logs one upstream deprecation warning under Airflow 3.3.1, but imports and execution pass.

Airflow metadata retains two serialized versions of `ecommerce_hourly` (marker baseline and current Cosmos graph), so `airflow dags list` prints two historical rows. The `dag` table contains one identity and public API contract validation selects the current 11-task version; no metadata history was deleted.
