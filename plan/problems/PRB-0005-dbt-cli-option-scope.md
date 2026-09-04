# PRB-0005 — Общие dbt CLI-флаги имеют разную область действия

Status: resolved  
Detected: 2026-09-04  
Resolved: 2026-09-04

## Symptom

После успешного reseed `make dbt-version` завершился с exit code `2`: dbt отверг `--project-dir`, добавленный Make wrapper-ом перед `--version`.

## Reproduction and evidence

```text
docker compose run --rm --no-deps dbt \
  --project-dir /workspace --profiles-dir /workspace --version
Error: No such option '--project-dir'.
```

## Root cause

В dbt 1.10 параметры project/profile доступны не для всех форм CLI, поэтому единый wrapper не может безусловно ставить их перед каждой командой.

## Attempted fixes

Перестановка флагов отдельно для каждой подкоманды возможна, но дублирует уже заданный container contract.

## Accepted fix

Wrapper оставляет только `docker compose run --rm --no-deps dbt`. Image задаёт `WORKDIR=/workspace` и `DBT_PROFILES_DIR=/workspace`, а project bind mount расположен там же.

## Regression check

Полная последовательность `dbt --version`, `debug`, `parse`, `compile`, `build`, `test` должна проходить через один Make wrapper.

## Follow-up

Если появятся несколько dbt projects, передавать пути в конкретных targets и покрывать каждую форму CLI отдельным smoke test.
