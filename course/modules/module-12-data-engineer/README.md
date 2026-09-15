# 12 — DE: ограниченная автономия изменения данных

Status: outline; lecture not written

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0012-data-engineer.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[10](../../modules/module-10-pm-specification/README.md), [8](../../modules/module-08-dbt-semantics/README.md)

## Теоретические outcomes

- Объяснить implementation authority, предпосылки и ограничения.
- Объяснить candidate change boundary, предпосылки и ограничения.
- Объяснить semantic repair, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `implementation authority`, `candidate change boundary`, `semantic repair`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Разделить утверждённую спецификацию и пространство допустимых implementation choices.
- Объяснить isolated candidate и authority только над editable dbt subtree.
- Показать Net Revenue payment/refund attribution как применение grain/semantics из 08/10.
- Рассмотреть semantic repair по validator evidence; не переобъяснять QA, reducer budget и checkpoint.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: runtime/data_engineer.py; runtime/data_engineer_workflow.py; STEP-0009

- [runtime/data_engineer.py](../../../runtime/data_engineer.py)
- [runtime/data_engineer_workflow.py](../../../runtime/data_engineer_workflow.py)
- [plan/evidence/STEP-0009-autonomous-data-engineer.md](../../../plan/evidence/STEP-0009-autonomous-data-engineer.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [What is analytics engineering?](https://www.getdbt.com/blog/what-is-analytics-engineering) — Transformation work как инженерная дисциплина.
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — Инкрементальный прогресс без необоснованного completion.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Будущий текст: `course/lectures/LECTURE-0012-data-engineer.md`; outline не лекция.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
