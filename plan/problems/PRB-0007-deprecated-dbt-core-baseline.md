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

Переход сразу на Core 1.12 был отклонён как выход за проверенный scope опубликованного adapter release. В immutable changelog для [`dbt-clickhouse` 1.10.2](https://github.com/ClickHouse/dbt-clickhouse/blob/c2eca075e47c3cc7b17b261a0b35a2954fd178d4/CHANGELOG.md#release-1101-2026-06-16) переход local test dependencies на Core 1.11 относится к release 1.10.1, а не 1.10.2. README того же [release commit](https://github.com/ClickHouse/dbt-clickhouse/blob/c2eca075e47c3cc7b17b261a0b35a2954fd178d4/README.md) заявляет feature support только до Core 1.10, поэтому full Core 1.11 compatibility не утверждается.

## Accepted fix

Зафиксирован [`dbt-core==1.11.14`](https://pypi.org/project/dbt-core/1.11.14/) вместе с опубликованным [`dbt-clickhouse==1.10.2`](https://pypi.org/project/dbt-clickhouse/1.10.2/); hash lock и image пересобраны. Эта связка локально проверяется только для используемого baseline feature set. Core 1.12 и неиспользуемые Core 1.11 features остаются вне текущего scope.

## Regression check

Historical local artifacts сообщают, что `dbt --version`, `debug`, `parse`, `compile`, `build` и `test` завершились с exit code `0`, deprecated-version warning исчез, build дал `PASS=76`, отдельный test — `PASS=68`, а independent SQL smoke — `dbt baseline: PASS`. После reseed `build` и `test` были повторены успешно. Source revision, точные timestamps и persistent output transcript этого прогона не были сохранены, поэтому fresh regression transcript остаётся pending в STEP-0002.

## Follow-up

Проверять одновременно adapter feature support и Core support window при каждом dependency review; не выбирать только по совпадению minor номера пакетов.
