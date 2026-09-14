# STEP-0023 — Operational observability backend evidence

Date: 2026-09-14

Status: PASS

## Delivered boundary

- Explicit non-global OTLP/HTTP runtime exporter accepts only a loopback origin, ignores proxy
  environment and batches with bounded queue/timeout.
- Digest-pinned Collector 0.160.0 applies memory/batch processing and whole-trace tail sampling:
  errors are kept, healthy traces are sampled at 25%. Spanmetrics exposes only low-cardinality
  role/model/tool/stage/receipt dimensions.
- Tempo 3.0.3 uses local persistent blocks with 72h scheduler/worker retention. Prometheus 3.14.0
  uses 7d and 1GB bounds. Grafana 13.2.1 provisions non-editable Tempo/Prometheus datasources and
  the `agentic-operational-overview` dashboard.
- All host ports bind to `127.0.0.1`; backend traffic shares an internal network. Each service has
  a separate host bridge needed by Docker 28 publication. Observability containers receive neither
  `API_TOKEN` nor Docker socket.

## Verification

| Command | Result |
| --- | --- |
| pinned Tempo `-config.verify=true` | exit 0 |
| `make observability-test` | exit 0; 15 passed; Compose valid |
| `make observability-smoke` twice with preserved volumes | both exit 0; Tempo trace, fresh process-local sampling counter, Prometheus series/two healthy targets, Grafana provisioning |
| `make check` | exit 0; Ruff PASS; format 151 files; 437 tests; plan governance and Compose PASS |
| `git diff --check` | exit 0 |
| resolved Compose/container secret and Docker-socket scans | PASS |
| `docker compose --profile observability ps --format json` | exit 0; empty after smoke |

Final repeated-smoke trace ID: `0b630d51206ae37bdefe7a04e0b871b9`. Named `tempo-data`,
`prometheus-data`, and `grafana-data` volumes remain present; no volume was removed. GateLLM and the
Data Platform were not invoked.

## Problems and remaining risks

PRB-0047 records the Tempo 3.0 retention schema correction; PRB-0048 records Docker 28 internal
network port behavior; PRB-0049 makes repeated smoke deterministic with preserved Prometheus state.
This is a single-host development stack without TLS, HA, alerts or external object storage. Grafana
credentials are dev-only, healthy-trace sampling is probabilistic, and Phase K must measure
evaluation behavior separately from operational telemetry.
