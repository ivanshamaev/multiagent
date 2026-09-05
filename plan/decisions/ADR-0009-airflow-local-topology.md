# ADR-0009 — Локальная топология Airflow и API boundary

Status: accepted  
Date: 2026-09-05

## Context

Golden Data Platform требует исполняемый Airflow 3 baseline, но официальный Compose quick-start с Celery/Redis избыточен для одного Ubuntu host. Будущий agent interface должен опираться на стабильный public API, не на UI или metadata DB. Airflow не должен получать GateLLM secret или небезопасный Docker socket.

## Decision

Используем `apache/airflow:3.3.1-python3.12` и `postgres:16.15-bookworm`, закреплённые multi-arch digest. Минимальная топология: PostgreSQL, one-shot init, API Server, Scheduler с `LocalExecutor`/`parallelism=2` и обязательный Dag Processor. API публикуется только на loopback; PostgreSQL port не публикуется.

Для воспроизводимого local development используем FAB Auth Manager и init-only dev admin. Программный gate получает JWT через `POST /auth/token`, затем работает только с stable `/api/v2`. JWT, API и Fernet secrets передаются allowlist-переменными; `.env` целиком не подключается. DAG использует только public `airflow.sdk`.

`ecommerce_hourly` на этом шаге является исполняемым orchestration contract: шесть deterministic стадий проверяют scheduling, dependency order и API run lifecycle. Он ещё не вызывает dbt. Безопасный dbt runner interface проектируется отдельно; Docker socket запрещён.

## Alternatives

- CeleryExecutor, Redis, worker, Flower и triggerer отклонены как ненужные baseline-компоненты.
- Simple Auth Manager проще, но официально предназначен только для test/dev и сохраняет/generated password в plaintext; FAB даёт детерминированный init/API flow.
- Встраивание dbt в Airflow image рискует dependency conflicts; DockerOperator потребовал бы privileged socket. Оба варианта отложены.
- CLI, UI scraping и прямой SQL к metadata DB отклонены как будущий agent contract.

## Consequences and validation

Стек остаётся локальным, не production-ready и требует одинаковых JWT/API secrets у API Server и Scheduler. Scheduler ждёт healthy API перед task execution. Gate проверяет image fingerprint, component JSON health, отсутствие import errors, unauthenticated rejection, JWT access и успешный six-task DAG run. Primary references: [Airflow Docker Compose](https://airflow.apache.org/docs/apache-airflow/3.3.1/howto/docker-compose/index.html), [configuration](https://airflow.apache.org/docs/apache-airflow/3.3.1/configurations-ref.html), [public API](https://airflow.apache.org/docs/apache-airflow/3.3.1/security/api.html), [security model](https://airflow.apache.org/docs/apache-airflow/3.3.1/security/security_model.html).
