# ADR-0011 — Оркестрация dbt через Astronomer Cosmos

Status: accepted

Date: 2026-09-05

Supersedes: ADR-0010 для построения dbt-графа, запуска команд и сбора task status. Решение об отдельном dbt virtualenv сохраняется.

## Context

Первая реализация STEP-0004 создала собственный subprocess runner и вручную разбила dbt-проект на слои. Это дублирует готовую интеграцию Airflow/dbt и требует самостоятельно поддерживать selection, artifacts, retries и соответствие графа dbt.

## Decision

Используем pinned `astronomer-cosmos==1.15.0`, стабильный релиз с поддержкой Airflow 3. Cosmos устанавливается без изменения существующих зависимостей Airflow; `pip check` остаётся обязательным. dbt Core/ClickHouse остаются в отдельном hash-locked `/opt/airflow/dbt-venv`.

`DbtTaskGroup` строит Airflow-граф из dbt lineage. Выбираем `ExecutionMode.LOCAL` + явный путь к изолированному dbt executable для render и runtime. `TestBehavior.AFTER_ALL` создаёт финальный dbt test gate, `full_refresh` и `fail_fast` задаются оператору. Исходный dbt-проект и profiles остаются read-only; generated output пишет Cosmos во временный writable workspace.

Проверка готовности deterministic seed остаётся отдельной upstream Airflow task. `publish` зависит от всего Cosmos task group, поэтому ошибка модели или теста закрывает публикацию. Negative probe использует штатный Cosmos test operator с неизменяемым failing project. API smoke проверяет фактический Cosmos graph/task states и отсутствие `publish` после failure.

## Consequences

Airflow UI отражает dbt lineage на уровне моделей вместо искусственных шести marker stages. Количество task instances становится производным от manifest и проверяется осмысленными обязательными nodes, а не старым фиксированным числом. Обновление Cosmos выполняется только отдельным ADR и повторным compatibility gate.

Источники: официальные руководства Cosmos по [local execution](https://astronomer.github.io/astronomer-cosmos/guides/run_dbt/airflow-worker/local-execution-mode.html), [dependency isolation](https://astronomer.github.io/astronomer-cosmos/guides/dbt_setup/execution-modes-local-conflicts.html), [test behavior](https://astronomer.github.io/astronomer-cosmos/guides/translate_dbt_to_airflow/testing-behavior.html) и [Airflow 3 compatibility](https://astronomer.github.io/astronomer-cosmos/policy/airflow3-compatibility.html).
