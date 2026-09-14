# STEP-0021 — Phase J: OpenTelemetry trace chain

Status: completed

Owner: Codex

Updated: 2026-09-14

## Goal

Получить один проверяемый OpenTelemetry trace для цепочки `workflow → role → model/tool → artifact`
с workflow/task/operation correlation, usage/latency/status и безопасным продолжением после role
checkpoint. Trace не должен содержать prompts, model output, tool arguments/results или secrets.

## Non-goals

- logs/metrics, production sampling и alerting;
- Collector/Jaeger deployment и dashboard UX;
- отдельные runner identities, filesystem/network isolation и MCP authentication;
- платный GateLLM или Data Platform smoke.

Backend deployment отделён от instrumentation: этот шаг создаёт стандартные SDK spans и exporter
boundary, к которому OTLP backend подключается без изменения role/model/tool кода.

## Affected layers and allowed paths

- runtime: `runtime/telemetry.py`, role pipeline, model provider и MCP gateway;
- dependency/config: `pyproject.toml`, `uv.lock`, `Makefile`;
- tests: `tests/{unit,integration,workflow,adversarial}/`;
- ledger/docs: `plan/`, `README.md`, `AGENTS.md`, `Claude.md`.

`contracts/`, reducer, role prompts, platform, scenarios и grader не изменяются.

## Acceptance criteria

1. Pinned OTel SDK создаёт spans с одним trace ID и иерархией workflow → role → model/tool/artifact.
2. Role spans фиксируют executor, input/output stage, workflow/task IDs, operation ID, receipt hit,
   status и exception type без exception message/stacktrace.
3. Model spans содержат только model/schema, usage, latency, finish reason и request/response hashes.
4. Tool spans содержат только tool/request/evidence IDs, arguments hash, status, duration и bytes.
5. Artifact spans содержат ID/type/producer и accepted event hash; content/evidence body отсутствуют.
6. Sanitized JSON exporter использует закрытый attribute allowlist, repository containment,
   0700/0600 и bounded append; неизвестные атрибуты и symlink/escape отклоняются.
7. Error и receipt-cache paths корректно помечаются; tracing failure не раскрывает payload.
8. `make telemetry-test` и `make check` проходят; Docker остаётся остановлен.

## Risks, permissions and approvals

- **Sensitive telemetry:** только typed API и allowlist; content recording всегда выключен.
- **Global SDK collisions:** использовать explicit `TracerProvider`, не менять global provider.
- **Exporter I/O failure:** fail closed для evidence smoke; runtime instrumentation не принимает
  произвольный путь/endpoint от агента.
- **High cardinality/volume:** bounded attributes, один artifact span на новый gate artifact,
  ограниченный file exporter.

Разрешены локальная установка pinned Python dependency через `uv` и subprocess tests. Сеть,
GateLLM, Docker writes, production backend и secrets не требуются.

## Checklist

- [x] Принять ADR-0030 о explicit safe OTel instrumentation.
- [x] Добавить pinned SDK и telemetry abstraction/exporter.
- [x] Инструментировать workflow/role и artifact acceptance.
- [x] Инструментировать GateLLM provider и MCP tool gateway.
- [x] Проверить hierarchy, attributes, errors, cache hit и redaction adversarial tests.
- [x] Выполнить targeted/full gates и записать evidence.

## Verification

- `make telemetry-test` — exit 0, 48 passed.
- `make role-pipeline-test` — exit 0, 13 passed.
- `make check` — exit 0, 406 passed; Ruff, format, plan governance и Compose config PASS.
- `docker compose ps --format json` — exit 0, пустой вывод.

Hierarchy, safe attributes, error redaction, receipt replay и exporter guards проверены assertions.

## Decisions and problems

- ADR-0030 создаётся до реализации.
- PRB-0043 фиксирует найденное при интеграции повторное создание artifact span на receipt hit.

## Work log

- 2026-09-14: шаг открыт; обнаружен transitive `opentelemetry-api==1.44.0`, SDK отсутствует.
- 2026-09-14: принят ADR-0030; добавлен pinned SDK и explicit content-free façade/exporter.
- 2026-09-14: workflow/role/model/tool/artifact instrumentation связана persisted trace carrier.
- 2026-09-14: `make telemetry-test` — 48 passed; `make role-pipeline-test` — 13 passed.
- 2026-09-14: полный gate 406/406; evidence сохранён, шаг завершён.
