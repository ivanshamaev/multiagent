# Каталог проблем

Для системной или нетривиальной проблемы создаётся `PRB-NNNN-short-name.md` со статусом, symptom, reproduction, evidence, root cause, attempted fixes, accepted fix, regression check и follow-up. Секреты и полный model output не записываются.

Последние записи: [PRB-0010](PRB-0010-custom-dbt-runner.md) заменяет custom dbt runner на Cosmos;
[PRB-0011](PRB-0011-cosmos-runtime-dependencies.md) фиксирует hash-locked runtime dependencies
Cosmos; [PRB-0012](PRB-0012-grader-workspace-permissions.md) исправляет read boundary non-root
grader; [PRB-0013](PRB-0013-openai3-httpx2-import.md) фиксирует смену HTTP package в OpenAI 3.
[`PRB-0014`](PRB-0014-gatellm-virtual-model-ids.md) документирует `~`-prefixed virtual model IDs.
[`PRB-0015`](PRB-0015-catalog-model-not-routable.md) добавляет live capability gate после catalog.
[`PRB-0016`](PRB-0016-schema-probe-and-model-reliability.md) заменяет text probe строгой schema
проверкой и фиксирует измеренный PM model override.
[`PRB-0017`](PRB-0017-fastmcp-update-egress.md) закрывает обнаруженный FastMCP update-check egress
через disabled update check и отдельную internal-only MCP network.
[`PRB-0018`](PRB-0018-dbt-mcp-schema-drift.md) синхронизирует локальные typed contracts с живыми
схемами pinned dbt MCP и добавляет регрессионную проверку сериализации gateway.
[`PRB-0019`](PRB-0019-docker-registry-dns.md) документирует восстановленный отказ
системного/VPN DNS, временно блокировавший повторную загрузку platform images.
[`PRB-0020`](PRB-0020-scenario-repro-false-green.md) исправляет ложный green reproducibility gate,
который ранее проглатывал ошибку `scenario-reset` и сравнивал две пустые строки.
[`PRB-0021`](PRB-0021-maf-handler-name-collision.md) фиксирует конфликт имени role handler с
framework-owned `Executor.execute`, обнаруженный offline end-to-end workflow test.
[`PRB-0022`](PRB-0022-capability-probe-premature-abort.md) разрешает cost-first selector
продолжить bounded поиск после schema-invalid HTTP 200 с сохранением usage.
[`PRB-0023`](PRB-0023-agent-model-tool-capability.md) добавляет отдельный function-calling gate:
strict schema support не гарантирует поддержку OpenAI-compatible tools.
[`PRB-0024`](PRB-0024-zero-tool-completion.md) классифицирует model completion без единого tool
evidence и сохраняет usage вместо неинформативного runtime `TypeError`.
[`PRB-0025`](PRB-0025-tool-argument-recovery-and-run-retention.md) даёт модели bounded recovery
после ошибочных tool arguments и гарантирует terminal run record для framework/provider failure.
[`PRB-0026`](PRB-0026-gatellm-tool-history-limit.md) фиксирует воспроизводимый HTTP 400 на третьем
tool-dialogue round текущего GateLLM/Llama route и требует phased fresh-conversation execution.
[`PRB-0027`](PRB-0027-parallel-tool-call-fanout.md) запрещает parallel tool fan-out в required
phase и сужает live budget после фактического пакета из 80 повторяющихся вызовов.
[`PRB-0028`](PRB-0028-tool-history-response-format.md) отделяет local Pydantic validation от
несовместимого provider schema mode при финализации tool-history.
[`PRB-0029`](PRB-0029-decorated-structured-output.md) извлекает только один однозначный
schema-valid JSON object из model decoration и отклоняет ambiguous output.
[`PRB-0030`](PRB-0030-capability-probe-rate-amplification.md) добавляет catalog-bound TTL cache
для успешных schema/tool probes и устраняет два лишних provider calls на каждый repeat run.
