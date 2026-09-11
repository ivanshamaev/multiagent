# Журнал прогресса

Записи добавляются по факту; планируемая работа сюда не попадает.

## 2026-09-04 — Инициализация проекта

- Проверены `init/init_build_multi_agent_system.md` и `init/init_cource_plan.md`; подробный build-план принят как основной implementation backlog, course plan — как целевое педагогическое представление.
- Проверено окружение: Ubuntu, Python 3.12.3, Docker 28.1.1, Docker Compose 2.35.1, GNU Make 4.3.
- Установлен `uv 0.12.9` в `/home/ivan/.local/bin` официальным standalone installer.
- Принята гибридная runtime-модель: agents/orchestrator локально в `.venv`; Data Platform в Docker Compose.
- Созданы структура `plan/`, подробный roadmap и начальные ADR.
- Проверен GateLLM `/v1/models` без вывода секрета; принят `inclusionai/ling-2.6-flash` как текущий cheapest CHAT default, с обязательным capability gate перед agent calls.
- Первый bootstrap-шаг завершён; актуальный active step указан ниже.

## 2026-09-04 — STEP-0001 завершён

- Созданы `pyproject.toml`, `uv.lock`, Python 3.12 `.venv`, Ruff/pytest config и канонические package-каталоги.
- Созданы Docker Compose/Make interfaces и ClickHouse 25.8.33.6 с loopback ports и healthcheck.
- Детерминированный seed создаёт 7 raw-таблиц и edge cases: cancellations, currencies, split payments, partial/multiple/late refunds, NULL channels и duplicate attribution.
- Пройдены `uv sync --frozen`, `make check` (5 tests), `make seed`, `make platform-test`; повторный seed/build state успешен.
- Зафиксированы и закрыты PRB-0001…PRB-0003.
- Следующий активный шаг: `STEP-0002-dbt-baseline.md`.

## 2026-09-05 — STEP-0002 завершён

- Добавлен одноразовый dbt runner в Docker Compose; Python image закреплён digest, Core/adapter и все transitive dependencies закреплены версиями и hashes.
- Реализованы 7 raw sources, 4 staging views, 2 intermediate views и 2 MergeTree marts без вычисления Net Revenue.
- Добавлены 68 generic/singular tests и независимый ClickHouse smoke с точными counts/aggregates.
- Пройдены `dbt debug → parse → compile → build → test`, повторный build без reset и полный reseed/build; persistent summary — `plan/evidence/STEP-0002-dbt-baseline.md`.
- Исправлены и закрыты PRB-0004…PRB-0008; deprecated Core 1.10 заменён проверенной связкой Core 1.11.14 + adapter 1.10.2, generated dbt user id удалён из repository state.
- Следующий активный шаг: `STEP-0003-airflow-baseline.md`.

## 2026-09-05 — STEP-0003 завершён

- Airflow 3.3.1 и PostgreSQL 16.15 запущены в Docker; images закреплены digest, LocalExecutor ограничен двумя процессами. API Server, Scheduler и Dag Processor имеют healthchecks.
- DAG `ecommerce_hourly` использует public Task SDK и исполняет цепь шести marker tasks. Фактический dbt execution ещё не реализован; следующий STEP-0004 посвящён этой интеграции.
- API smoke проверяет 401 без JWT, authenticated access, component health, exact task dependencies и success всех шести task instances. Два свежих run IDs сохранены в STEP-0003 transcript.
- Независимый review обнаружил дефекты HTTP/polling/error handling в проверяющем скрипте; fixes и regression tests записаны в PRB-0009.
- Пройдены `make -s platform-up`, `make -s airflow-test`, повторный `make -s airflow-init`, `make -s platform-test`; все exit 0. `make check` — Ruff, 20 pytest и Compose PASS.
- STEP-0002 повторно проверен после evidence audit: fresh full transcript, source checksum, timestamps, 76 build results/68 tests и independent SQL assertions сохранены.
- `API_TOKEN` отсутствует в resolved Compose config и actual Data Platform containers. GateLLM completion calls не выполнялись. Существующие Docker volumes и чужие образы не удалялись.
- Актуальный следующий шаг: `STEP-0004-airflow-dbt-execution.md` (planned). Остаток диска после pull — около 2.3 GiB; перед следующим image build проверить повторно.

## 2026-09-05 — STEP-0004 завершён

- По уточнению пользователя custom dbt runner заменён Astronomer Cosmos 1.15.0; решение и migration rationale записаны в ADR-0011 и PRB-0010.
- Cosmos `DbtTaskGroup` строит dbt lineage из восьми моделей и запускает единый `AFTER_ALL` test gate через изолированный dbt virtualenv. Scheduled DAG остаётся paused; acceptance использует manual twin.
- Три API runs завершились 11/11 success и прошли independent SQL. Negative Cosmos test дал `dbt_tests=failed`, `publish=upstream_failed`; baseline не изменился.
- `make platform-test` подтвердил raw assertions, 68 dbt tests и mart assertions. `make check` — 32 tests; API_TOKEN отсутствует в Data Platform.
- Persistent summary и transcript: `plan/evidence/STEP-0004-airflow-cosmos.md`. Следующий активный шаг: `STEP-0005-scenario-harness.md`.

## 2026-09-05 — STEP-0005 завершён

- Добавлены versioned manifest/schema и transactional allowlisted snapshot для `net-revenue`;
  основной checkout, `.env`, `.git`, planning/runtime и grader source в workspace не попадают.
- Два полных reset дали одинаковые source/workspace/ClickHouse fingerprints и baseline dbt result.
- Public `scenario-run` отделён от hidden grader. Grader работает non-root, read-only, без Docker
  socket/API token и только во внутренней сети ClickHouse; baseline ожидаемо имеет `INCOMPLETE`.
- 60 pytest checks покрывают traversal, symlink, unmanaged target, protected edit, stale source,
  contamination recovery и isolation policy. PRB-0012 исправил mode managed workspace.
- `make platform-test` после network change: Airflow/Cosmos 11/11 success, 68 dbt tests и SQL PASS.
- Evidence: `plan/evidence/STEP-0005-scenario-harness.md`. LLM calls и удаление volumes не выполнялись.
- Следующий активный шаг: `STEP-0006-contracts-state-machine.md`.

## 2026-09-06 — STEP-0006 завершён

- Реализованы frozen/closed Pydantic v1 contracts для request, specification, analysis,
  implementation, validation, QA, review и content-addressed evidence.
- Pure reducer проверяет полную transition matrix, role/task/authorship gates и bounded budgets;
  исчерпанный rework детерминированно заканчивается `FAILED` без превышения лимита.
- Canonical hash chain обнаруживает mutation, reorder, replay и truncation относительно ожидаемого
  state. MAF/provider SDK не связан с domain contracts.
- `make check` — 101 tests; scenario fingerprints воспроизведены; isolated baseline grader PASS;
  `make platform-test` — Airflow/Cosmos 11/11, dbt 68/68 и SQL PASS.
- Evidence: `plan/evidence/STEP-0006-contracts-state-machine.md`. LLM calls не выполнялись.
- Следующий активный шаг: `STEP-0007-local-agent-runtime.md`.

## 2026-09-06 — STEP-0007 завершён

- Добавлен GateLLM provider через pinned MAF Chat Completions adapter: secret-safe settings,
  bounded retries/timeouts, cost/config model selection, schema capability probe и fake transport.
- Controlled PM Agent читает только проверенный content-addressed scenario context, формирует
  строгий draft и передаёт artifact/usage существующему reducer; prompts/raw responses не хранятся.
- Cost comparison выявил 404/504/schema failures дешёвых моделей; Llama 3.1 8B прошла полный smoke
  за ~0.02583 ₽ и зафиксирована как датированный PM default (PRB-0013–0016, EXP-0001).
- `make check` — 129 tests; scenario fingerprints и baseline grader воспроизведены;
  `make platform-test` — Airflow/Cosmos 11/11, dbt 68/68 и SQL PASS.
- Evidence: `plan/evidence/STEP-0007-local-agent-runtime.md`. Следующий активный шаг:
  `STEP-0008-tool-policy-layer.md`.

## 2026-09-11 — STEP-0008 завершён

- Официальные ClickHouse/dbt MCP изолированы в pinned stdio containers; ClickHouse identity имеет
  только SELECT на `raw.*`/`analytics.*`, а dbt работает только с verified scenario project.
- Typed contracts, SQLGlot AST gate, capability profile, atomic workspace adapter, cumulative MCP
  budgets и content-addressed evidence образуют deny-by-default boundary вне prompts.
- MAF видит только локальный facade; invalid arguments и policy denial завершают loop через
  `MiddlewareFailure`. Live smoke прошёл query + dbt compile/test и отклонил DDL до MCP.
- После восстановления удалённых Docker images: Airflow/Cosmos 11/11, dbt 68/68, scenario и grader
  воспроизведены; `make check` — 210 tests. PRB-0017–0020 сохраняют найденные проблемы и fixes.
- Evidence: `plan/evidence/STEP-0008-tool-policy-layer.md`. Следующий planned шаг:
  `STEP-0009-autonomous-data-engineer.md`.

## 2026-09-11 — STEP-0009 в работе: control-plane slice

- Human-authored Net Revenue specification зафиксирована по scenario version и SHA-256 `TASK.md`;
  identity, evidence и workflow transitions исключены из model-owned draft.
- Data Engineer получает verified/delimited context и 13 profile tools. Workspace и official MCP
  вызовы теперь используют единый serialized tool/wall/output ledger.
- Bounded MAF tool loop и code-owned artifact assembly доводят offline execution до `IMPLEMENTED`;
  self-reported completion без фактического dbt diff закрывается как `FAILED`.
- `make check` — 227 tests, Ruff/format и Compose validation PASS. Платные LLM calls не выполнялись.
- Следующий блок STEP-0009: независимый deterministic validator и negative fixtures.
