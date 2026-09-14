# ADR-0032 — Local OpenTelemetry operational stack

Status: accepted

Date: 2026-09-14

## Context

STEP-0021 создаёт стандартные content-free OTel spans и hardened JSONL evidence, но не даёт query,
retention, service metrics или dashboard. Нужен reproducible local backend без превращения
development stack в production distributed system.

## Decision

Использовать pinned OpenTelemetry Collector Contrib как единственный ingestion/processing point,
Grafana Tempo с local persistent storage для traces, Prometheus для Collector/span metrics и
Grafana с file-provisioned datasources/dashboard. OTLP/HTTP и UIs публикуются только на loopback;
backend traffic идёт по отдельной internal Docker network.

Collector всегда сохраняет traces с ERROR status и probabilistically сохраняет 25% остальных
complete traces. Spanmetrics connector получает sampled trace stream и экспортирует только
low-cardinality dimensions; task/workflow/request/artifact identifiers остаются trace-only. Batch и
memory limiter ограничивают ingestion. Tempo block retention — 72h, Prometheus retention — 7d.

Runtime использует explicit OTLP HTTP exporter factory с validated `http://127.0.0.1:<port>` base
endpoint. Environment-driven auto instrumentation и глобальный provider остаются запрещены.

## Alternatives

- Jaeger all-in-one: отклонён для этого slice из-за менее явной local block retention/metrics
  topology; Tempo естественно интегрируется с provisioned Grafana.
- Direct SDK → Tempo: отклонён, так как теряются central sampling, memory/batch policy и spanmetrics.
- Elasticsearch/Loki/Mimir/object storage: отложены как несоразмерные single-host prototype.
- 100% sampling: отклонено как плохой operational default; error-always policy сохраняет failures.

## Consequences and validation

Stack добавляет четыре Docker images и три named volumes, но не зависит от Data Platform. Local
volumes являются bounded-by-time operational storage, не signed audit evidence. Smoke обязан
создать error trace, дождаться tail decision, подтвердить его через Tempo, metric через Prometheus и
provisioning через Grafana API, затем остановить только observability services без `-v`.
