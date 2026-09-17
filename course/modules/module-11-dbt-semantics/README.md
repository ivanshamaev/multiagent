# 11 — dbt, lineage и семантика аналитической модели

Status: reviewed; full lecture published

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0011-dbt-semantics.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

[Читать лекцию 11](../../lectures/LECTURE-0011-dbt-semantics.md)

## Место и prerequisites

[10](../../modules/module-10-analytical-sql/README.md)

## Теоретические outcomes

- Объяснить model grain, предпосылки и ограничения.
- Объяснить transformation lineage, предпосылки и ограничения.
- Объяснить dbt validation stages, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `model grain`, `transformation lineage`, `dbt validation stages`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Определить grain и зависимость staging/intermediate/marts без курса общего SQL.
- Разобрать lineage и parse/compile/build/test: разные kinds of evidence.
- Развести warehouse model graph, Airflow DAG и multi-agent control graph.
- Показать Cosmos как интеграцию dbt в data orchestration, не писать инструкции развёртывания.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: platform/dbt/; platform/airflow/dags/cosmos_pipeline.py; STEP-0004

- [platform/airflow/dags/cosmos_pipeline.py](../../../platform/airflow/dags/cosmos_pipeline.py)
- [plan/evidence/STEP-0004-airflow-cosmos.md](../../../plan/evidence/STEP-0004-airflow-cosmos.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [What is analytics engineering?](https://www.getdbt.com/blog/what-is-analytics-engineering) — Analytics transformation как инженерная ответственность.
- [Why data testing is essential for analytics engineering](https://www.getdbt.com/blog/data-testing) — Data assertions в transformation lifecycle.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Текст: `course/lectures/LECTURE-0011-dbt-semantics.md`.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
