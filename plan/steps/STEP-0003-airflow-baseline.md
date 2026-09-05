# STEP-0003 — Airflow baseline

Status: done  
Owner: primary agent  
Updated: 2026-09-05  
Current step: завершён; следующий — STEP-0004, фактическое выполнение dbt

## Goal

Добавить воспроизводимый Airflow 3.3.1 с PostgreSQL state, `LocalExecutor`, DAG `ecommerce_hourly` и end-to-end проверкой stable public `/api/v2` через JWT. Шаг доказывает импорт DAG, работу всех шести стадий и API-first управление.

## Non-goals

- Не монтировать Docker socket и не давать Airflow доступ к `API_TOKEN`.
- Не встраивать dbt dependencies в Airflow image и не выдавать structural DAG за фактический dbt execution.
- Не реализовывать Airflow MCP, production auth/HA, Celery, Redis, triggerer или observability.
- Не удалять существующие Docker volumes/images/cache и не менять `init/**`.

## Affected layers and allowed paths

Разрешены `docker-compose.yml`, `Makefile`, `.env.example`, `.gitignore`, `platform/airflow/**`, `tests/**`, `plan/**`, `README.md`, `AGENTS.md` и `Claude.md`. dbt models, ClickHouse seed, local agent runtime и LLM provider остаются без изменений.

## Acceptance criteria

- [x] Airflow/PostgreSQL images закреплены version + multi-arch digest; Compose не использует `latest`.
- [x] PostgreSQL не публикует port, Airflow API доступен только на `127.0.0.1:8080`.
- [x] `airflow-init` идемпотентно мигрирует metadata DB и создаёт dev-only FAB admin.
- [x] API Server, Scheduler и Dag Processor проходят собственные healthchecks; LocalExecutor ограничен `parallelism=2`.
- [x] DAG использует public `airflow.sdk`, содержит ровно цепочку `load_raw → dbt_staging → dbt_intermediate → dbt_marts → dbt_tests → publish` и не содержит import errors.
- [x] Документация явно говорит, что текущие стадии проверяют orchestration contract, но ещё не исполняют dbt.
- [x] Неавторизованный API request отклонён; JWT получается без вывода credentials/token.
- [x] API smoke запускает уникальный DAG run, bounded-poll завершается `success`, все шесть task instances успешны.
- [x] `make check`, dbt/ClickHouse regression gate и общий `make platform-test` завершаются с exit code `0`.
- [x] Для каждого gate сохранены timestamp, command, exit code и sanitized output reference.

## Risks, permissions, and approvals

- На host свободно около 5.3 GiB; pull останавливается и фиксируется как problem до любой очистки чужих Docker assets.
- Официальный Compose quick-start предназначен только для development; credentials в `.env.example` не подходят для shared/production среды.
- DAG-файлы — исполняемый Python. В будущем agent-authored DAG нельзя монтировать в активный scheduler до deterministic validation.
- `/api/v2/monitor/health` возвращает HTTP 200 даже при unhealthy component; smoke проверяет JSON statuses.
- API/JWT/Fernet secrets передаются явным allowlist. Compose не использует `env_file: .env`.

## Steps

1. [x] Проверить current stable release, official Compose/OpenAPI и image digests.
2. [x] Зафиксировать topology, auth и integration boundary в ADR-0009.
3. [x] Добавить Compose services, volumes, healthchecks и Make interface.
4. [x] Реализовать публичный-SDK DAG и статические policy tests.
5. [x] Реализовать bounded API v2 smoke без утечки JWT/password.
6. [x] Выполнить init/start/import/API/run gates и повторный init/run.
7. [x] Повторить ClickHouse/dbt regression и полный platform gate.
8. [x] Сохранить evidence, проблемы, remaining risks и обновить статус.

## Verification and evidence

| Command | Expected | Actual |
| --- | --- | --- |
| `docker compose config --quiet` | exit 0 | exit 0 |
| `make -s airflow-version` | Airflow 3.3.1 | exit 0; 3.3.1 |
| `make -s platform-up` | healthy services + completed init | exit 0; ClickHouse + four Airflow/PostgreSQL services healthy |
| `make -s airflow-test` | import/health/auth/API run PASS | exit 0; six tasks successful, exact edges checked |
| `make -s airflow-init` | idempotent | exit 0; existing user retained |
| `make -s platform-test` | no regressions | exit 0; second DAG run 6/6, dbt 68/68, SQL suites PASS |
| `make check && git diff --check` | exit 0 | exit 0; 20 Python tests, Ruff/Compose/whitespace clean |

Persistent [summary](../evidence/STEP-0003-airflow-baseline.md) и [полный transcript](../evidence/STEP-0003-fresh-transcript.md) сохранены в Git-visible `plan/evidence/`; финальные local checks — в [handoff record](../evidence/STEP-0003-local-checks.md). Транскрипты содержат timestamps, run IDs, exit codes и scoped source fingerprint.

## Decisions and problems

- Topology/auth/API boundary: ADR-0009.
- Problems: PRB-0009 — исправлены redirect/deadline/secret-reflection и CLI exit-code propagation в acceptance smoke; regression tests добавлены.
- Remaining risk: безопасный runner interface между Airflow и отдельным dbt container проектируется отдельным шагом.

## Work log

- 2026-09-05: создан step до implementation edits; проверены official Airflow 3.3.1 Compose, configuration, health, security и OpenAPI contracts.
- 2026-09-05: выбран минимальный LocalExecutor topology без Redis/Celery/triggerer; интеграция dbt сознательно отделена от orchestration smoke.
- 2026-09-05: скачаны закреплённые images, schema migration/init завершились с exit 0; первый API-driven six-task run успешен.
- 2026-09-05: независимый review выявил дефекты проверяющего кода; PRB-0009 исправлена и покрыта deterministic tests.
- 2026-09-05: fresh gate 03:57:08–04:00:45 UTC подтвердил повторный init, два DAG runs, dbt/SQL regression и отсутствие API_TOKEN в actual containers. STEP-0003 закрыт.

## Remaining risks

Полный pipeline пока не выполняет dbt из Airflow — это STEP-0004. FAB выводит upstream deprecation/in-memory rate-limit warnings; текущий stack предназначен для локального development. Повторный init не меняет пароль существующего пользователя. После загрузки images осталось около 2.3 GiB диска; перед следующим image build необходимо повторно проверить запас. Named task logs требуют будущей retention policy; Docker stdout logs уже ограничены 10 MiB × 3 на Airflow container.
