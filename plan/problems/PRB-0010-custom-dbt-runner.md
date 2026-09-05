# PRB-0010 — Самописный dbt runner дублировал Cosmos

Status: resolved

Date: 2026-09-05

## Symptom and reproduction

Первая реализация STEP-0004 вручную строила пять стадий, argv, artifacts и publish evidence в `dbt_pipeline.py`. Review выявил ошибки порядка dbt CLI flags, writable log path, stale artifacts и неполную проверку seed.

## Root cause

Интеграция повторяла обязанности специализированного Airflow/dbt проекта. Чем сильнее становился custom runner, тем больше поведения dbt и Airflow приходилось воспроизводить и тестировать локально.

## Accepted fix

ADR-0011 заменил runner на pinned Astronomer Cosmos 1.15.0. `DbtTaskGroup` строит задачи из dbt lineage и запускает dbt через изолированный executable. В проекте осталась только независимая readiness task и publish boundary. Добавлен manual acceptance DAG, чтобы проверка не снимала pause с `@hourly` DAG.

## Regression check

Repository policy требует `DbtTaskGroup`, LOCAL/SUBPROCESS, `AFTER_ALL` и отсутствие custom `subprocess` в DAG helper. Public API smoke проверяет exact 11-task Cosmos graph; independent SQL проверяет результат.
