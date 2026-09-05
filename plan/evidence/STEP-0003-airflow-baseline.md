# Evidence — STEP-0003 Airflow baseline

Captured: 2026-09-05, 03:57:08–04:00:45 UTC.

## Configuration fingerprint

Base commit: `4e5c70a1f5a46943db8a43405c6bb3ae0b8b8930`, with uncommitted changes. Runtime source checksum: `13e8a3ab803f5278f98cb0eeb800bbcfc466dc395e5ce02d0162cd62353f3846`; scope and exact command are retained in the [full transcript](STEP-0003-fresh-transcript.md).

- Airflow image: `apache/airflow:3.3.1-python3.12@sha256:b01a795dfbd113bbbfdf3ee169b8f27e9a0090ccef105f1a452b3594a11ed316`.
- PostgreSQL image: `postgres:16.15-bookworm@sha256:bb3e1a57e5407e0a5280b4211980a5e537f4abd234a87014ac979849a78dd825`.
- LocalExecutor: parallelism 2; FAB auth; public API on loopback; internal PostgreSQL; read-only DAG mount.

## Acceptance results

All commands below returned exit code `0`; timestamps and complete output are retained in the transcript.

| Command | UTC interval | Observed result |
| --- | --- | --- |
| `make -s airflow-version` | 03:57:08–03:57:18 | 3.3.1 |
| `make -s platform-up` | 03:57:18–03:58:46 | ClickHouse, PostgreSQL, API, scheduler and DAG processor healthy |
| `make -s airflow-test` | 03:58:46–03:59:29 | imports clean, unauthenticated 401, JWT auth, exact edges, 6/6 tasks success |
| `make -s airflow-init` | 03:59:29–03:59:55 | migration and existing-user initialization idempotent |
| `make -s platform-test` | 03:59:55–04:00:45 | second Airflow run 6/6; dbt 68/68; raw and mart SQL assertions PASS |
| resolved config + actual container inspection | 04:00:45 | API_TOKEN absent; PostgreSQL has no published port; exposed endpoints loopback-only |

Successful run IDs:

- `api_smoke_20260905T035915613875Z_87837881`
- `api_smoke_20260905T040025501011Z_4eb212b8`

[Local checks](STEP-0003-local-checks.md) retain Ruff, 20 pytest tests, Compose validation and whitespace checks. The deterministic regressions cover failed run handling, secret reflection, redirect rejection, timeout exhaustion, wrong/duplicate task definitions and CLI exit propagation.

## Meaning and limits

These runs prove Airflow orchestration and API lifecycle only. The DAG tasks are markers; the dbt/SQL suites run separately in the same platform gate. Actual dbt execution inside the DAG is planned in STEP-0004 and Phase A remains incomplete until then. No GateLLM completion was requested. Upstream FAB deprecation and local rate-limit storage warnings did not fail the gate.
