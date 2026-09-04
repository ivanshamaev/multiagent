# ADR-0001 — Гибридный runtime

Status: accepted  
Date: 2026-09-04

## Context

Agents и workflow требуют быстрого edit/test/debug цикла. ClickHouse, dbt, Airflow и их state должны запускаться одинаково на разных Ubuntu-машинах.

## Decision

Microsoft Agent Framework, orchestrator, agent runtime, contracts и pytest запускаются локально в `.venv`, управляемом `uv` на Python 3.12. Data Platform — ClickHouse, dbt runner, Airflow, PostgreSQL и observability — запускается в Docker Compose. Make targets скрывают детали Compose.

## Alternatives

- Всё в Docker: воспроизводимо, но замедляет локальную итерацию и debugging Python runtime.
- Всё на host: быстрее начать, но трудно воспроизводить версии platform services.

## Consequences and validation

Нужно явно описать host/container networking, credentials и version pins. Gate: `uv sync --frozen` и Compose baseline проходят на чистой машине по documented commands.

