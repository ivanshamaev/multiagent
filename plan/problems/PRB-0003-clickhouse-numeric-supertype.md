# PRB-0003 — Нет общего типа Int64/UInt64 в seed expression

Status: resolved  
Detected: 2026-09-04  
Resolved: 2026-09-04

## Symptom

После исправления alias повторный `make seed` дошёл до вычисления `selected_order_id`, но ClickHouse вернул server code `386` (`NO_COMMON_TYPE`): ветви `if` смешивали `Int64` и `UInt64`. После локального исправления refund insert прошёл, а тот же дефект проявился в `source_number` для duplicate attribution rows.

## Root cause

`numbers()` выдаёт `UInt64`, а арифметика с неявно типизированными integer literals и вычитанием привела к signed/unsigned ветвям, для которых ClickHouse не выбирает небезопасный общий тип.

## Attempted fix

Первоначальное приведение всех literals к `UInt64` не помогло: ClickHouse типизирует вычитание `UInt64 - UInt64` как signed result, а `intDiv` снова получил несовместимые аргументы.

## Accepted fix

Вычислять потенциально отрицательную промежуточную арифметику второй ветви в `Int64`, затем явно приводить готовый положительный identifier к `UInt64`. Паттерн применён к refund и attribution generators. Тип refund `if` предварительно проверен отдельным `toTypeName(...)` запросом и равен `UInt64`.

## Regression check

`make seed` повторно завершился с exit code `0`; `make platform-test` подтвердил `10,000` refunds, `1,000` order ids с несколькими refund rows и duplicate attribution events.
