# PRB-0004 — `dbt debug` не находит git в slim-образе

Status: resolved  
Detected: 2026-09-04  
Resolved: 2026-09-04

## Symptom

`make dbt-debug` подтвердил корректные profile/project files и соединение с ClickHouse, но завершился с exit code `1`: dependency check не нашёл команду `git` в `python:3.12.14-slim-bookworm`.

## Reproduction and evidence

```text
make dbt-version dbt-debug dbt-parse dbt-compile
Required dependencies: git [ERROR]
Connection test: [OK connection ok]
make: dbt-debug Error 1
```

## Root cause

dbt проверяет `git` как runtime dependency для package workflows, а минимальный Python image не включает его по умолчанию.

## Attempted fixes

Флаг `dbt debug --connection` позволил бы пропустить dependency checks, но скрыл бы неполный runtime image и не соответствовал полному acceptance gate.

## Accepted fix

В dbt image добавлен `git` через `apt-get install --no-install-recommends`; apt metadata удаляется в том же layer. Build context ограничен `platform/dbt/` и `.dockerignore`, поэтому локальный `.env` с `API_TOKEN` не передаётся builder-у.

## Regression check

Повторный полный `make dbt-debug` должен завершиться с exit code `0`; результат записывается в STEP-0002.

## Follow-up

Сохранять полный `dbt debug`, а не только connection-only shortcut, в baseline validator.
