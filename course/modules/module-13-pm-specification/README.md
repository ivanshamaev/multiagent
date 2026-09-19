# 13 — PM: формальная спецификация и пределы знания

Status: reviewed; content and visual publication gates passed

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0013-pm-specification.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

[Читать лекцию 13](../../lectures/LECTURE-0013-pm-specification.md)

## Место и prerequisites

[12](../../modules/module-12-analyst-provenance/README.md)

## Теоретические outcomes

- Объяснить business metric definition, предпосылки и ограничения.
- Объяснить requirements readiness, предпосылки и ограничения.
- Объяснить needs-user semantics, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `business metric definition`, `requirements readiness`, `needs-user semantics`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Развести business intent, data fact и проверяемое acceptance criterion.
- Объяснить authority PM над semantics, но не над фактами/permissions.
- Разобрать assumptions и material unknowns; почему NEEDS_USER — корректное решение.
- Показать human-authored Net Revenue spec и реальный unresolved handoff; не обещать live READY.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: runtime/specification.py; scenarios/net-revenue/specification.json; STEP-0013

- [runtime/specification.py](../../../runtime/specification.py)
- [scenarios/net-revenue/specification.json](../../../scenarios/net-revenue/specification.json)
- [plan/evidence/STEP-0013-pm-specification-gate.md](../../../plan/evidence/STEP-0013-pm-specification-gate.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Build and centralize metrics with the dbt Semantic Layer](https://www.getdbt.com/blog/build-centralize-and-deliver-consistent-metrics-with-the-dbt-semantic-layer) — Согласованность определений метрик.
- [Data Mesh Principles and Logical Architecture](https://martinfowler.com/articles/data-mesh-principles.html) — Потребительские требования к data product.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Текст: `course/lectures/LECTURE-0013-pm-specification.md`.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
