# Agentic Data Platform

Практический reference project для построения команды AI-агентов, которая выполняет задачи Data Engineering в управляемом workflow. После стабилизации системы её решения, traces, эксперименты и failure records станут основой курса.

## Текущий статус

Реализованы golden Data Platform, reproducible scenario harness, strict typed artifacts и
детерминированный workflow с budgets и hash-chained events, read-only Analyst, tool-free PM gate и
GET-only Airflow MCP под отдельным Viewer и controlled trigger одного dev-DAG под отдельной identity.
Runtime работает локально в Python 3.12 `.venv`, управляемом `uv`; Data Platform запускается в
Docker Compose. LLM-вызовы идут через OpenAI-совместимый GateLLM с токеном из локального `.env`.
Phase J содержит hardened MAF checkpoint storage и six-role checkpointable pipeline.
Работают ClickHouse,
контейнерный dbt baseline, Airflow 3.3.1 с Astronomer Cosmos 1.15.0 и PostgreSQL 16.15.

Актуальный roadmap: [`plan/development-plan.md`](plan/development-plan.md). Фактически выполненная работа: [`plan/progress.md`](plan/progress.md).

## Быстрый старт

Требования: Ubuntu, Docker Engine с Compose v2, GNU Make, Python 3.12 и `uv 0.12.9`.

```bash
test -f .env || cp .env.example .env
make bootstrap
make check
make platform-up
make seed
make dbt-build
make platform-test
```

`make llm-catalog` безопасно обновляет metadata без completion. `make requirements-live` — явный
платный вертикальный smoke `Analyst → PM`; модели задаются `ANALYST_MODEL` и `PM_MODEL`. Команда не
печатает prompt, model output или token, а сохраняет только sanitised metrics. `make llm-smoke`
оставлен как совместимый alias этого pipeline.

`make airflow-mcp-smoke` создаёт acceptance run детерминированным admin-клиентом, затем читает DAG,
run, task instances и bounded log только через локальный MCP под `airflow_observer`. MCP не содержит
trigger/pause/clear/retry, connection/variable/XCom или произвольных HTTP операций.

`make airflow-trigger-approve TASK_ID=<task> IDEMPOTENCY_KEY=<key> APPROVED_BY=<person>` создаёт
короткоживущий одноразовый approval. Отдельный trigger MCP принимает только
`ecommerce_acceptance`, сам выводит стабильный run ID и всегда отправляет пустой `conf`.
`make airflow-trigger-smoke` временно unpause-ит manual DAG test-fixture, доказывает повтор без
дубликата и гарантированно возвращает paused-состояние.

`make checkpoint-smoke` не вызывает LLM или Data Platform: он завершает первую стадию
двухшагового MAF graph, дожидается durable checkpoint, убивает процесс через `SIGKILL` и
восстанавливает pending вторую стадию в новом процессе. Счётчики подтверждают отсутствие
повторного выполнения уже committed стадии.

`make role-pipeline-test` проверяет шесть отдельных MAF executors (`Analyst → PM → DE → Validator
→ QA → Reviewer`), typed JSON handoffs и новый процесс, продолжающий работу после DE без повторного
запуска завершённых ролей. Тест детерминированный и не вызывает LLM или Data Platform.

ClickHouse публикуется только на loopback-интерфейсе. HTTP и native endpoints по умолчанию доступны на `127.0.0.1:8123` и `127.0.0.1:9000`.

`make dbt-build` создаёт 6 views и 2 MergeTree marts и выполняет 68 tests. `make platform-test` проверяет Airflow через API, повторяет dbt tests и независимо проверяет физические таблицы и фиксированные агрегаты. Net Revenue намеренно отсутствует: это будущая benchmark-задача Data Engineer Agent.

## Scenario harness

Benchmark `net-revenue` запускается только в disposable workspace; основной checkout не меняется:

```bash
make scenario-reset SCENARIO=net-revenue
make scenario-status SCENARIO=net-revenue
# После изменений агента в показанном workspace:
make scenario-run SCENARIO=net-revenue
make scenario-grade SCENARIO=net-revenue
```

Reset повторно загружает fixture data, строит baseline и фиксирует logical checksums. `scenario-run`
видит только public task и dbt project. Hidden grader работает non-root в отдельном read-only
container и не исполняет submission code. На неизменённом baseline он ожидаемо возвращает JSON
`INCOMPLETE`; regression target `make scenario-grade-baseline-test` трактует это как успешную
проверку boundary. `make scenario-repro-test` доказывает совпадение двух полных reset.

Airflow UI доступен на `http://127.0.0.1:8080`; локальные defaults — пользователь `airflow`, пароль `airflow_dev_only`. PostgreSQL не публикует host port. DAG `ecommerce_hourly` строится Cosmos из dbt lineage и остаётся paused по умолчанию; `make airflow-test` запускает его manual twin и проверяет JWT, exact 11-task graph и результат SQL. Подробнее: [`platform/airflow/README.md`](platform/airflow/README.md).

Образы Airflow и PostgreSQL занимают примерно 2.8 GB дополнительно к ClickHouse/dbt; оставляйте запас для данных и логов. Существующий `.env` не перезаписывайте: он может содержать `API_TOKEN`.

Остановить сервисы без удаления данных:

```bash
make platform-down
```

## Основные каталоги

- `orchestrator/`, `contracts/` — готовые artifact gates, workflow reducer и event integrity.
- `runtime/`, `agents/`, `policies/` — развиваемые agent adapters, execution и authorization.
- `platform/` — контейнеризованная Data Platform.
- `scenarios/`, `grader/` — public benchmark contracts и изолированный hidden oracle.
- `tests/` — unit, integration, workflow, policy и adversarial checks.
- `plan/` — обязательные планы, ADR, проблемы, эксперименты и журнал прогресса.
- `init/` — исходные архитектурные материалы; это не статус реализации.

Все credentials в `.env.example` предназначены только для локальной разработки. Не используйте их в shared или production environment.
