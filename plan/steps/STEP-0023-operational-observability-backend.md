# STEP-0023 — Phase J: operational observability backend

Status: completed

Owner: Codex

Updated: 2026-09-14

## Goal

Превратить content-free spans STEP-0021 в локальный operational observability stack: OTLP export,
Collector processing/tail sampling, span-derived metrics, bounded retention и provisioned dashboard.
Trace/task investigation должна воспроизводиться одной smoke-командой без GateLLM/Data Platform.

## Non-goals

- production HA/object storage, TLS/OIDC, multi-tenant isolation и remote ingestion;
- logging pipeline, Alertmanager/on-call integration и external notification;
- запись prompts, completions, tool payload или exception messages;
- Phase K repeated LLM benchmark и изменение agent prompts/models;
- удаление Docker volumes или запуск основной Data Platform.

## Affected layers and allowed paths

- runtime/export: `runtime/telemetry.py`, `runtime/observability_smoke.py`, dependencies;
- stack/config: `docker-compose.yml`, `observability/{otel,tempo,prometheus,grafana}/**`, `Makefile`;
- verification: `tests/{unit,integration,policy,adversarial}/`;
- ledger/runbooks: `plan/`, `README.md`, `AGENTS.md`, `Claude.md`.

Не изменяются contracts, reducer, role prompts, platform datasets, scenarios и grader.

## Acceptance criteria

1. Runtime имеет explicit opt-in OTLP/HTTP exporter с validated loopback endpoint, bounded timeout
   и тем же content-free façade; глобальный provider/env auto-instrumentation запрещены.
2. Pinned Collector принимает OTLP только через loopback-published endpoint, применяет memory/batch
   и tail sampling: error traces сохраняются всегда, healthy traces sampled 25%.
3. Span metrics не содержат workflow/task/request/artifact IDs; разрешены только low-cardinality
   span name, status, role/model/tool/stage и receipt-hit dimensions.
4. Pinned Tempo хранит traces в local volume с 72h block retention; Prometheus хранит metrics 7d;
   storage не публикуется наружу и volumes не удаляются stop-командой.
5. Pinned Grafana получает provisioned Tempo/Prometheus datasources и read-only dashboard для
   throughput, errors, p95 latency, role/model/tool breakdown и sampling/collector health.
6. Live smoke создаёт error trace без sensitive content, находит trace в Tempo, span metric в
   Prometheus и dashboard/datasources в Grafana; credentials/token не печатаются и не попадают в
   telemetry containers.
7. Config/policy/adversarial tests, `make observability-smoke` и `make check` проходят; после smoke
   observability services остановлены, volumes сохранены.

## Risks, permissions and approvals

- Docker pull/start разрешены только для четырёх pinned observability images; Data Platform и
  GateLLM не используются. Остановка scope ограничена observability services, volumes не удаляются.
- Tail sampling требует память до decision timeout; memory limiter и local single-user bounds
  обязательны. Smoke использует error trace для детерминированного keep.
- Grafana local dev credentials не являются production secret; bind только loopback. `API_TOKEN`
  не передаётся ни одному observability service.
- High-cardinality IDs остаются в traces для correlation, но исключены из Prometheus labels.

## Implementation checklist

- [x] Принять ADR-0032 о Collector + Tempo + Prometheus + Grafana и retention/sampling policy.
- [x] Добавить pinned OTLP exporter и validated runtime factory.
- [x] Добавить hardened Compose topology и backend/provisioning configs.
- [x] Создать operational dashboard и deterministic no-LLM live smoke.
- [x] Добавить unit/policy/adversarial tests для endpoint, config, cardinality и secret boundary.
- [x] Выполнить targeted/live/full gates, остановить services и сохранить evidence.

## Verification

Фактически: `make observability-test` — 15 passed; `make observability-smoke` — trace/metric/
sampling/health/dashboard PASS; `make check` — 437 passed; `git diff --check` и Compose config —
exit 0. После smoke список running observability services пуст, три named volumes сохранены.

## Decisions and problems

- ADR-0032 создаётся до implementation.
- Систематические defects получают PRB с reproduction/fix/regression.

## Work log

- 2026-09-14: шаг открыт; latest official releases проверены через GitHub API.
- 2026-09-14: зафиксированы manifest digests Collector 0.160.0, Tempo 3.0.3, Prometheus 3.14.0,
  Grafana 13.2.1 для linux/amd64 multi-platform manifests.
- 2026-09-14: PRB-0047 исправил несовместимые Tempo 2.x fields; встроенная config verification
  pinned 3.0.3 image прошла.
- 2026-09-14: PRB-0048 сохранил internal backend network и восстановил loopback publication через
  отдельные одно-сервисные host bridges.
- 2026-09-14: PRB-0049 устранил false timeout повторного smoke на сохранённой Prometheus series;
  fresh sampling decision проверяется на loopback Collector metrics, независимо от WAL history.
- 2026-09-14: targeted, live и full gates прошли; evidence сохранён, сервисы остановлены без
  удаления volumes. Phase J завершена, следующий этап — Phase K evaluation benchmark.
