# Evidence — STEP-0021 OpenTelemetry trace chain

Date: 2026-09-14

Status: PASS

## Delivered boundary

- Pinned `opentelemetry-sdk==1.44.0` behind an explicit, non-global tracer provider.
- One trace hierarchy: `agentic.workflow → agentic.role → agentic.model|tool|artifact`.
- Typed checkpoint carrier retains only trace ID and workflow span ID; role restart restores parent.
- Model/tool integrations export usage, latency, state and hashes, never request/response content.
- Sanitized JSONL exporter enforces a closed schema, repository containment, 0700/0600 and 20 MB.
- Receipt retries produce a cache-hit role span and do not duplicate accepted artifact spans.

## Verification record

| Command | Exit | Result |
| --- | ---: | --- |
| `make telemetry-test` | 0 | 48 passed |
| `make role-pipeline-test` | 0 | 13 passed |
| `make check` | 0 | Ruff PASS; format PASS; 406 tests; plan/Compose PASS |
| `docker compose ps --format json` | 0 | empty; no running project containers |

The tests use an in-memory exporter and fake model/MCP transports, so no `API_TOKEN`, GateLLM cost,
network request, Docker service or production system was involved.

## Decisions, defects and remaining risk

- ADR-0030: repository-owned explicit safe OTel instrumentation.
- PRB-0043: artifact span duplication on role receipt replay, fixed and regression-tested.
- The SDK is instrumented, but Collector/OTLP storage, sampling, retention and dashboards remain
  intentionally deferred. Local JSONL traces are integrity evidence, not signed audit records.
- The next Phase J step must introduce runner identities plus filesystem/network/MCP isolation;
  tracing does not itself enforce permissions.
