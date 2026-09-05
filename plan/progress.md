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
