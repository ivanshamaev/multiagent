# 01 — Декомпозиция ответственности и организация команды

Status: outline; lecture not written

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0001-organization.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[00](../../modules/module-00-agentic-baseline/README.md)

## Теоретические outcomes

- Объяснить role decomposition, предпосылки и ограничения.
- Объяснить task coupling, предпосылки и ограничения.
- Объяснить separation of duties, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `role decomposition`, `task coupling`, `separation of duties`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Сформулировать критерии разделения задачи: связность, разнородность знаний и ownership результата.
- Развести role name и действительную ответственность/capability; не считать число агентов мерой качества.
- Объяснить конфликт решений при разделении зависимого engineering work.
- Показать Analyst/PM/DE/QA/Reviewer как различные полномочия, не подробно разбирать их алгоритмы.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: policies/profiles/; ADR-0003/0006; STEP-0008

- [plan/evidence/STEP-0008-tool-policy-layer.md](../../../plan/evidence/STEP-0008-tool-policy-layer.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Data Mesh Principles and Logical Architecture](https://martinfowler.com/articles/data-mesh-principles.html) — Ownership данных как аналогия, не доказательство Data Mesh.
- [Don’t Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents) — Согласованность решений при разделении инженерной работы.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Текст написан и опубликован в STEP-0031: [лекция 01](../../lectures/LECTURE-0001-organization.md).
Этот файл сохраняет outline для планирования; reader выбирает полный текст по manifest/receipts.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
