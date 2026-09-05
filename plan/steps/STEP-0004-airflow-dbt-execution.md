# STEP-0004 — Фактическое выполнение dbt из Airflow

Status: planned  
Owner: primary agent  
Updated: 2026-09-05  
Current step: запланирован после завершения STEP-0003

## Goal

Заменить marker tasks в `ecommerce_hourly` реальными операциями над текущим dbt baseline. Успешный DAG run должен означать построенные модели, пройденные tests и независимые SQL assertions. Это завершает Phase A перед scenario harness.

## Non-goals and allowed paths

Без Net Revenue, MCP, LLM calls, production credentials и Docker socket. Разрешены `platform/airflow/**`, конфигурация контейнеров/Make, подходящие tests и `plan/**`. `init/**`, исходный seed и независимые expected SQL assertions сохраняются.

## Acceptance criteria

- [ ] Перед реализацией новый ADR сравнивает отдельный runner interface и изолированный dbt venv внутри Docker; обновляет boundary ADR-0009 при необходимости.
- [ ] Airflow и dbt не делят конфликтующий Python dependency graph; применён существующий hash-locked dbt requirements.
- [ ] `load_raw` проверяет готовность seed; destructive fixture reset не запускается по hourly schedule.
- [ ] Staging, intermediate и marts действительно строятся, полный dbt test gate исполняется до publish.
- [ ] dbt project смонтирован read-only, target/log output направлен в отдельный writable path.
- [ ] Ошибка dbt task делает DAG failed и исключает publish; имеется независимый negative test.
- [ ] Два API-triggered runs успешны; independent SQL smoke подтверждает counts/aggregates после каждого.
- [ ] Повторный `make platform-test`, local checks и secret isolation проходят с persistent evidence.

## Risks

Версии Airflow constraints и dbt lock различаются; устанавливать dbt в environment Airflow нельзя. На текущем host мало свободного диска: до нового image build проверить объём; чужие images/cache/volumes без разрешения не удалять. Hourly schedule должен оставаться paused до готовности данных и успешного ручного gate.

## Implementation steps

1. Измерить доступные ресурсы, проверить dependency constraints и выбрать runner boundary в ADR.
2. Создать воспроизводимый image/runner, проверить оба dependency graphs и versions.
3. Подключить реальные stage commands, timeouts и read-only mounts.
4. Добавить fail-before-publish regression и выполнить API-driven positive/negative gates.
5. Сохранить timestamps, run IDs, dbt invocation IDs, output references и SQL assertions.
6. Обновить документацию и только затем перейти к Phase B.

## Verification

Команды формируются в начале active iteration; предполагаемые targets не объявляются рабочими. Базовые обязательные gates: `make check`, `make seed`, `make dbt-build`, `make airflow-test`, `make platform-test`, `git diff --check`.
