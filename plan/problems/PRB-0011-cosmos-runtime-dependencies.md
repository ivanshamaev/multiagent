# PRB-0011 — Неполная установка Cosmos с `--no-deps`

Status: resolved

Date: 2026-09-05

## Symptom and reproduction

Первый image build с `astronomer-cosmos==1.15.0` завершился exit code 1: `pip check` сообщил отсутствующие `aenum` и `deprecation`.

## Root cause

Cosmos устанавливался с `--no-deps`, чтобы pip не изменил dependency graph digest-pinned Airflow image. Две обязательные runtime-зависимости отсутствовали в базовом образе.

## Accepted fix

В `platform/airflow/requirements.lock` добавлены exact versions и PyPI wheel hashes для Cosmos, `aenum` и `deprecation`. Установка остаётся `--no-deps --require-hashes`, затем выполняется `python -m pip check`.

## Regression check

`make airflow-version` проверяет Airflow environment, импорт/версию Cosmos и отдельный dbt environment. Fresh build завершился успешно: Airflow 3.3.1, Cosmos 1.15.0, dbt Core 1.11.14, dbt-clickhouse 1.10.2.
