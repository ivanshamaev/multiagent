# PRB-0007 — Первоначальный dbt Core baseline уже deprecated

Status: validating  
Detected: 2026-09-04

## Symptom

Каждая команда с первоначально выбранным `dbt-core==1.10.23` предупреждала, что minor version deprecated и больше не получает регулярные patches, хотя все functional tests проходили.

## Reproduction and evidence

```text
make dbt-version
installed: 1.10.23
latest: 1.12.3
This version of dbt is deprecated and no longer receives regular patches.
```

## Root cause

Версия была выбрана консервативно по feature-level совместимости адаптера 1.10, но без проверки текущего support window dbt Core.

## Attempted fixes

Переход сразу на Core 1.12 отклонён: поддержка этой ветки в `dbt-clickhouse` ещё выделена в отдельную upstream work item. Официальный changelog адаптера 1.10.2 сообщает о переходе его test matrix на Core 1.11.

## Candidate fix

Зафиксировать последний patch поддерживаемой ветки `dbt-core==1.11.14`, пересобрать hash lock/image и повторить весь `debug → parse → compile → build → test` gate на ClickHouse 25.8.

## Regression check

Pending: отсутствие deprecated-version warning и повторяемый полный platform gate.

## Follow-up

Проверять одновременно adapter feature support и Core support window при каждом dependency review; не выбирать только по совпадению minor номера пакетов.
