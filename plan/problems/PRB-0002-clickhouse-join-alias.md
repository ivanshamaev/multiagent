# PRB-0002 — ClickHouse требует alias для table function в JOIN

Status: resolved  
Detected: 2026-09-04  
Resolved: 2026-09-04

## Symptom

Первый `make seed` завершился с exit code `2`/server code `206` (`ALIAS_REQUIRED`) при вставке `raw.refunds`.

## Reproduction and evidence

ClickHouse 25.8.33 выполнил предыдущие statements, затем отклонил `FROM numbers(10000) INNER JOIN raw.orders ...`: для table function не был указан alias. Полный server message содержал `joined_subquery_requires_alias`.

## Root cause

Seed-запрос использовал table function `numbers(10000)` в `JOIN` без явного alias, что запрещено текущей строгой конфигурацией ClickHouse.

## Accepted fix

Источник изменён на `FROM numbers(10000) AS generated`. Seed идемпотентно пересоздаёт `raw`, поэтому повторный запуск не зависит от частично выполненной первой попытки.

## Regression check

`make seed` должен завершаться с exit code `0`; `make platform-test` проверяет точное количество refund rows и multiple-refund edge case.

