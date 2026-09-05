# Agentic Data Platform

Практический reference project для построения команды AI-агентов, которая выполняет задачи Data Engineering в управляемом workflow. После стабилизации системы её решения, traces, эксперименты и failure records станут основой курса.

## Текущий статус

Реализуется foundation-слой. Agent runtime будет работать локально в Python 3.12 `.venv`, управляемом `uv`; Data Platform запускается в Docker Compose. Все будущие LLM-вызовы пойдут через OpenAI-совместимый GateLLM с токеном из локального `.env`. Работают ClickHouse, контейнерный dbt baseline и Airflow 3.3.1 с Astronomer Cosmos 1.15.0 и PostgreSQL 16.15. Agent runtime пока не реализован.

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

ClickHouse публикуется только на loopback-интерфейсе. HTTP и native endpoints по умолчанию доступны на `127.0.0.1:8123` и `127.0.0.1:9000`.

`make dbt-build` создаёт 6 views и 2 MergeTree marts и выполняет 68 tests. `make platform-test` проверяет Airflow через API, повторяет dbt tests и независимо проверяет физические таблицы и фиксированные агрегаты. Net Revenue намеренно отсутствует: это будущая benchmark-задача Data Engineer Agent.

Airflow UI доступен на `http://127.0.0.1:8080`; локальные defaults — пользователь `airflow`, пароль `airflow_dev_only`. PostgreSQL не публикует host port. DAG `ecommerce_hourly` строится Cosmos из dbt lineage и остаётся paused по умолчанию; `make airflow-test` запускает его manual twin и проверяет JWT, exact 11-task graph и результат SQL. Подробнее: [`platform/airflow/README.md`](platform/airflow/README.md).

Образы Airflow и PostgreSQL занимают примерно 2.8 GB дополнительно к ClickHouse/dbt; оставляйте запас для данных и логов. Существующий `.env` не перезаписывайте: он может содержать `API_TOKEN`.

Остановить сервисы без удаления данных:

```bash
make platform-down
```

## Основные каталоги

- `orchestrator/`, `runtime/`, `agents/` — будущий local agent control plane.
- `contracts/`, `policies/` — typed artifacts и deterministic authorization.
- `platform/` — контейнеризованная Data Platform.
- `tests/` — unit, integration, workflow, policy и adversarial checks.
- `plan/` — обязательные планы, ADR, проблемы, эксперименты и журнал прогресса.
- `init/` — исходные архитектурные материалы; это не статус реализации.

Все credentials в `.env.example` предназначены только для локальной разработки. Не используйте их в shared или production environment.
