# 07 — Аналитический SQL и ограниченные data capabilities

Status: outline; lecture not written

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0007-analytical-sql.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[6](../../modules/module-06-mcp-interface/README.md)

## Теоретические outcomes

- Объяснить analytical query scope, предпосылки и ограничения.
- Объяснить SQL resource envelope, предпосылки и ограничения.
- Объяснить read capability composition, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `analytical query scope`, `SQL resource envelope`, `read capability composition`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Объяснить metadata/profile/aggregate access и минимально достаточный SQL surface.
- Развести SELECT syntax, фактические side effects и использование функций/таблиц вне scope.
- Показать AST/policy query checks, row/time/output bounds и read-only database identity.
- Кратко связать materialization с видом наблюдаемых данных, не преподавать dbt или query tuning заново.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: policies/tool_policy.py; platform/clickhouse/security/; STEP-0008

- [policies/tool_policy.py](../../../policies/tool_policy.py)
- [plan/evidence/STEP-0008-tool-policy-layer.md](../../../plan/evidence/STEP-0008-tool-policy-layer.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Writing effective tools for agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — Специализированный tool вместо чрезмерно общего интерфейса.
- [Using Materialized Views in ClickHouse](https://clickhouse.com/blog/using-materialized-views-in-clickhouse) — Materialized analytical result как контекст наблюдения.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Будущий текст: `course/lectures/LECTURE-0007-analytical-sql.md`; outline не лекция.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
