# STEP-0004 — Фактическое выполнение dbt из Airflow

Status: active  
Owner: primary agent  
Updated: 2026-09-05  
Current step: изолированный dbt runner и API-driven positive/negative gates

## Goal

Заменить marker tasks в `ecommerce_hourly` реальными операциями над текущим dbt baseline. Успешный DAG run должен означать построенные модели, пройденные tests и независимые SQL assertions. Это завершает Phase A перед scenario harness.

## Non-goals and allowed paths

Без Net Revenue, MCP, LLM calls, production credentials и Docker socket. Разрешены `platform/airflow/**`, конфигурация контейнеров/Make, подходящие tests, contributor guides и `plan/**`. `init/**`, исходный seed, dbt lock и независимые expected SQL assertions сохраняются.

## Acceptance criteria

- [x] Перед реализацией ADR-0010 сравнивает отдельный runner interface и изолированный dbt venv внутри Docker; уточняет boundary ADR-0009.
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

## Implementation contract and verification details

- Pinned Airflow base + `/opt/airflow/dbt-venv`, installed at image build from existing hash-locked requirements. No runtime pip installs.
- Read-only dbt source mount; per-run/per-stage outputs in named `airflow-dbt-artifacts` volume; compact invocation/result metadata returned through XCom.
- `load_raw`: source tests; three dbt layer runs; `dbt_tests`: full test suite; `publish`: validate upstream evidence and expose in-place marts without copying data.
- Manual-only `ecommerce_failure_probe` uses the same pipeline factory, but points its validation task at a separate immutable fixture containing a guaranteed failing SQL test. It must produce failed run/failed dbt_tests/upstream_failed publish. It cannot modify baseline source or hidden expected values.
- API smoke explicitly unpauses only the local allowlisted DAG, restores its previous paused state, uses unique IDs and bounded polling. Hourly pipeline remains paused by default until operator opts in.
- Planned gate commands: `make airflow-image`, `make airflow-version`, `make platform-up`, `make seed`, `make airflow-test`, `make dbt-baseline-test`, repeated `make airflow-test`, `make airflow-failure-test`, `make platform-test`, `make check`.

## Work log

- 2026-09-05 12:25 UTC: confirmed user commit `cad4b38`, clean worktree and about 6.2 GiB free disk; STEP-0003 local check record restored. Airflow base contains Python 3.12.13, git, standard provider 1.17.0 and FAB 3.8.0.
- 2026-09-05: ADR-0010 accepted before implementation; two isolated dependency graphs selected for local Docker runtime.
