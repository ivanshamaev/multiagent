# ADR-0030 — Explicit safe OpenTelemetry instrumentation

Status: accepted

Date: 2026-09-14

## Context

MAF имеет собственные OTel hooks, но Data Platform должна связывать domain workflow, role receipts,
provider metadata, MCP evidence и accepted artifacts. Автоматическая GenAI instrumentation может
записывать prompts/completions или нестабильные framework attributes, а global tracer provider
создаёт конфликты в тестах и embedded runtime.

## Decision

Использовать pinned `opentelemetry-sdk` через repository-owned typed façade и explicit
`TracerProvider`. Фасад создаёт только пять span kinds: `agentic.workflow`, `agentic.role`,
`agentic.model`, `agentic.tool`, `agentic.artifact`. Domain identifiers и безопасные hashes
передаются как attributes; content, arguments, results, credentials, exception messages и
stacktraces запрещены.

Trace context создаётся в workflow wrapper и передаётся в immutable checkpoint snapshot. Role span
явно восстанавливает parent из этого carrier, поэтому restart может продолжить тот же trace ID.
Model/tool spans используют текущий role context. Artifact spans создаются только для новых
reducer-accepted artifacts.

Для детерминированного evidence применяется bounded sanitized JSON exporter с закрытым allowlist и
owner-only repository path. Он реализует стандартный OTel `SpanExporter`; OTLP Collector/Jaeger
подключается позднее заменой exporter, без изменения instrumentation.

## Alternatives

- Только MAF auto-instrumentation: отклонено из-за неполной domain correlation и content risk.
- Global provider/env-only setup: отклонено из-за process-wide side effects и неявной конфигурации.
- Custom tracing без OTel SDK: отклонено как несовместимый telemetry island.
- Collector/Jaeger в этом шаге: отложено; сначала проверяется безопасный span contract.

## Consequences and validation

Instrumentation требует явной передачи telemetry dependency, зато тестируется без сети и не
расходует LLM budget. Stable carrier становится частью checkpoint contract и требует новой graph
version. Hierarchy, resume trace ID, error sanitization и exporter guards проверяются тестами.
