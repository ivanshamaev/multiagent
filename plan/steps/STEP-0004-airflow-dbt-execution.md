# STEP-0004 — Фактическое выполнение dbt из Airflow

Status: complete
Owner: primary agent
Updated: 2026-09-05
Current step: complete; evidence сохранён, следующий шаг — STEP-0005

## Goal

Заменить marker tasks в `ecommerce_hourly` реальными операциями над текущим dbt baseline. Успешный DAG run должен означать построенные модели, пройденные tests и независимые SQL assertions. Это завершает Phase A перед scenario harness.

## Non-goals and allowed paths

Без Net Revenue, MCP, LLM calls, production credentials и Docker socket. Разрешены `platform/airflow/**`, конфигурация контейнеров/Make, подходящие tests, contributor guides и `plan/**`. `init/**`, исходный seed, dbt lock и независимые expected SQL assertions сохраняются.

## Acceptance criteria

- [x] ADR-0011 заменяет custom runner на Astronomer Cosmos, сохраняя изолированный dbt venv.
- [x] Airflow и dbt не делят конфликтующий Python dependency graph; применён существующий hash-locked dbt requirements.
- [x] `load_raw` проверяет готовность seed; destructive fixture reset не запускается по hourly schedule.
- [x] Staging, intermediate и marts действительно строятся, полный dbt test gate исполняется до publish.
- [x] dbt project смонтирован read-only; Cosmos выполняет каждую команду в writable temporary clone.
- [x] Ошибка dbt task делает DAG failed и исключает publish; имеется независимый negative test.
- [x] Два API-triggered runs успешны; independent SQL smoke подтверждает counts/aggregates после каждого.
- [x] Повторный `make platform-test`, local checks и secret isolation проходят с persistent evidence.

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

- Pinned Airflow base + pinned Cosmos in the Airflow environment; `/opt/airflow/dbt-venv` is installed at image build from the existing hash-locked requirements. No runtime installs.
- `DbtTaskGroup` owns model lineage and execution with `ExecutionMode.LOCAL`, explicit isolated executable and `TestBehavior.AFTER_ALL`; the dbt source mount stays read-only.
- `load_raw` runs deterministic seed-readiness SQL. Cosmos renders and runs staging, intermediate, marts and their final full test gate; `publish` is downstream from the complete task group.
- Manual-only `ecommerce_failure_probe` uses a Cosmos test operator and immutable guaranteed-failing fixture. It must fail before publish without changing baseline source or expected values.
- API smoke explicitly unpauses only the local allowlisted DAG, restores its previous paused state, uses unique IDs and bounded polling. Hourly pipeline remains paused by default until operator opts in.
- Planned gate commands: `make airflow-image`, `make airflow-version`, `make platform-up`, `make seed`, `make airflow-test`, `make dbt-baseline-test`, repeated `make airflow-test`, `make airflow-failure-test`, `make platform-test`, `make check`.

## Work log

- 2026-09-05 12:25 UTC: confirmed user commit `cad4b38`, clean worktree and about 6.2 GiB free disk; STEP-0003 local check record restored. Airflow base contains Python 3.12.13, git, standard provider 1.17.0 and FAB 3.8.0.
- 2026-09-05: ADR-0010 accepted before implementation; two isolated dependency graphs selected for local Docker runtime.
- 2026-09-05: user selected Astronomer Cosmos to avoid maintaining a custom dbt runner. ADR-0011 supersedes that part of ADR-0010 before live acceptance; Cosmos 1.15.0 LOCAL mode with isolated dbt executable selected from current official documentation.
- 2026-09-05 17:57–18:02 UTC: три manual Cosmos runs завершились 11/11 success; два требуемых повтора и дополнительный full platform gate подтверждены independent SQL.
- 2026-09-05 17:59 UTC: negative Cosmos test сделал DAG failed; `publish=upstream_failed`, baseline SQL остался green.
- 2026-09-05 18:06 UTC: STEP закрыт; версии, run IDs, task states, local gates и ограничения сохранены в `plan/evidence/STEP-0004-airflow-cosmos.md` и fresh transcript.

## Actual verification

`make airflow-version`, `make seed`, `make dbt-build`, два `make airflow-test`, `make airflow-failure-test`, `make platform-test`, `make check` и `git diff --check` завершились exit code `0`. Три positive run IDs и negative task states сохранены в evidence. Phase A завершена без LLM calls.
