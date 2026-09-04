# ADR-0004 — Стек Data Platform

Status: accepted  
Date: 2026-09-04

## Context

Курс должен воспроизводить реальную задачу аналитической платформы, но оставаться поднимаемым локально.

## Decision

Используем ClickHouse для аналитических данных, dbt для transformations/tests, Airflow 3 для orchestration и PostgreSQL для infrastructure state. Сервисы работают в Docker Compose. Будущий Airflow MCP использует public `/api/v2`, а не metadata DB.

## Alternatives

Kubernetes и managed cloud services отложены до стабильного Compose baseline. Прямой доступ к Airflow metadata DB запрещён.

## Consequences and validation

Версии образов фиксируются; сервисы имеют healthchecks и dev-only credentials. Golden gate — `make platform-up`, `make seed`, `make dbt-build`, `make platform-test`.

