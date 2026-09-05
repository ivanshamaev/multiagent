# Evidence — STEP-0002 dbt baseline

Recorded: 2026-09-05  
Evidence status: fresh gate captured  
Environment: Ubuntu, Docker 28.1.1, Compose 2.35.1

## Source and versions

Base commit: `4e5c70a1f5a46943db8a43405c6bb3ae0b8b8930`, with uncommitted changes. Scoped tree checksum for `platform/dbt` and `platform/clickhouse`: `a6ca3950b13d7b1c5e025f4374d01ab9c0054745a0b7ef051a1aaffbd42b4972`. The exact fingerprint command is in the transcript.

- ClickHouse: `clickhouse/clickhouse-server:25.8.33.6`.
- dbt image: `agentic-data-platform-dbt:1.11.14-1.10.2`, local ID `sha256:299b4b00e44db396a107eb575511d0f20b40c7120d8c9f5bed85f2dbd68a345b`.
- Python base: `python:3.12.14-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254`.
- Python graph: exact versions and hashes in `platform/dbt/requirements.lock`. Debian `git` remains unpinned; the full image is not bit-reproducible.
- Core 1.11.14 compatibility is demonstrated only for this baseline feature set, not every Core feature. See [PRB-0007](../problems/PRB-0007-deprecated-dbt-core-baseline.md) and the immutable [adapter changelog](https://github.com/ClickHouse/dbt-clickhouse/blob/c2eca075e47c3cc7b17b261a0b35a2954fd178d4/CHANGELOG.md#release-1101-2026-06-16).

## Fresh deterministic results

Every row links to the persistent [full transcript](STEP-0002-fresh-transcript.md), containing exact commands, start/end timestamps and exit codes. Earlier aggregate reports lacked these records; this fresh run replaces them as completion evidence.

| UTC interval on 2026-09-05 | Exact command | Result |
| --- | --- | --- |
| 03:50:10–03:51:27 | `make -s dbt-version dbt-debug dbt-parse dbt-compile` | exit 0; Core 1.11.14, adapter 1.10.2, connection/parse/compile PASS |
| 03:51:27–03:51:48 | `make -s dbt-build dbt-test clickhouse-test dbt-baseline-test` | exit 0; build PASS=76, tests PASS=68, both SQL suites PASS |
| 03:51:48–03:52:06 | `make -s dbt-build dbt-test` | exit 0; repeat without reset PASS=76/68 |
| 03:52:06–03:52:33 | `make -s seed dbt-build dbt-test clickhouse-test dbt-baseline-test` | exit 0; reseed, rebuild and independent assertions PASS |

Final dbt test invocation: `6d549709-c6c3-4e91-a992-967e5710e9c1`; `run_results.json` generated at `2026-09-05T03:52:31.170770Z`, 68 results, every status `pass`.

The independent SQL suites verify 100,000 order facts, 20,000 customers, 95,000 paid orders, 8,652 orders with successful refunds, 9,565 successful refund events, exact payment/refund aggregates, six views, two MergeTree marts, and absence of Net Revenue/temp relations.

The expanded platform gate and actual-container secret-isolation checks are retained in [STEP-0003 transcript](STEP-0003-fresh-transcript.md). No GateLLM completion request occurred.
