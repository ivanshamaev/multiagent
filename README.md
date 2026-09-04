# Agentic Data Platform

Практический reference project для построения команды AI-агентов, которая выполняет задачи Data Engineering в управляемом workflow. После стабилизации системы её решения, traces, эксперименты и failure records станут основой курса.

## Текущий статус

Реализуется foundation-слой. Agent runtime будет работать локально в Python 3.12 `.venv`, управляемом `uv`; Data Platform запускается в Docker Compose. Все LLM-вызовы будут идти через OpenAI-совместимый GateLLM gateway с токеном из локального `.env`. Сейчас доступен минимальный ClickHouse baseline. dbt, Airflow и агенты добавляются следующими изолированными шагами.

Актуальный roadmap: [`plan/development-plan.md`](plan/development-plan.md). Фактически выполненная работа: [`plan/progress.md`](plan/progress.md).

## Быстрый старт

Требования: Ubuntu, Docker Engine с Compose v2, GNU Make, Python 3.12 и `uv 0.12.9`.

```bash
cp .env.example .env
make bootstrap
make check
make platform-up
make seed
make platform-test
```

ClickHouse публикуется только на loopback-интерфейсе. HTTP и native endpoints по умолчанию доступны на `127.0.0.1:8123` и `127.0.0.1:9000`.

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
