# PRB-0006 — dbt profile использует устаревшее расположение flags

Status: resolved  
Detected: 2026-09-04  
Resolved: 2026-09-04

## Symptom

Успешные `dbt debug`, `parse` и `compile` печатали `ProjectFlagsMovedDeprecation`: user config в ключе `config` файла `profiles.yml` больше не является рекомендуемым.

## Reproduction and evidence

```text
make dbt-debug
User config should be moved from the 'config' key in profiles.yml
to the 'flags' key in dbt_project.yml.
```

## Root cause

`send_anonymous_usage_stats: false` был записан по старому profile convention, который dbt 1.10 ещё принимает только ради совместимости.

## Attempted fixes

Оставлять warning нецелесообразно: он скрывает будущие значимые deprecations и усложняет evidence.

## Accepted fix

Настройка перенесена в `flags` файла `dbt_project.yml`; устаревший `config` удалён из profile.

## Regression check

Повторные `dbt debug` и `dbt parse --no-partial-parse` не должны выдавать `ProjectFlagsMovedDeprecation`.

## Follow-up

После каждого upgrade запускать parse с отключённым partial parsing и отдельно проверять deprecation summary.
