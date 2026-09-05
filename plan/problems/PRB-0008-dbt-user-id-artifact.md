# PRB-0008 — Локальный dbt user id попал в репозиторий

Status: resolved
Detected: 2026-09-05
Resolved: 2026-09-05

## Symptom

После dbt-прогонов в `platform/dbt/.user.yml` сохранился generated UUID, и файл оказался tracked в bootstrap commit.

## Reproduction and evidence

`git ls-files platform/dbt/.user.yml` возвращал путь, а файл содержал единственное поле `id`. Значение не переносится в этот журнал.

## Root cause

dbt создал локальный user/telemetry artifact внутри bind-mounted project directory; исходный `.gitignore` учитывал `target/` и `logs/`, но не `.user.yml`.

## Accepted fix

Generated файл удалён, `.user.yml` добавлен в `.gitignore`, а repository policy test требует одновременно ignore rule и отсутствие project copy.

## Regression check

`make check` должен пройти, а `git status --short` не должен показывать новый `.user.yml` после dbt commands.

## Follow-up

Перед каждым handoff проверять новые dotfiles в bind-mounted tool projects и классифицировать их как source, local config или runtime artifact.
