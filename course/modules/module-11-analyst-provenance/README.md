# 11 — Analyst: discovery, lineage и provenance фактов

Status: outline; lecture not written

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0011-analyst-provenance.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[8](../../modules/module-08-dbt-semantics/README.md), [17](../../modules/module-17-state-memory/README.md)

## Теоретические outcomes

- Объяснить data fact provenance, предпосылки и ограничения.
- Объяснить semantic discovery, предпосылки и ограничения.
- Объяснить facts/assumptions distinction, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `data fact provenance`, `semantic discovery`, `facts/assumptions distinction`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Разобрать schema/lineage/profile как разные источники знания.
- Объяснить evidence-backed fact и ограничение вывода из sampled/aggregate data.
- Показать three fresh read phases и synthesis; не определять business metric вместо PM.
- Сопоставить доступность данных и достаточность для требования; не обещать anomaly investigation corpus.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: runtime/analyst.py; tests/fixtures/analyst_cases.json; STEP-0012

- [runtime/analyst.py](../../../runtime/analyst.py)
- [tests/fixtures/analyst_cases.json](../../../tests/fixtures/analyst_cases.json)
- [plan/evidence/STEP-0012-analyst-requirements-discovery.md](../../../plan/evidence/STEP-0012-analyst-requirements-discovery.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Data Mesh Principles and Logical Architecture](https://martinfowler.com/articles/data-mesh-principles.html) — Discoverability/understandability данных.
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Отбор релевантной информации для synthesis.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Будущий текст: `course/lectures/LECTURE-0011-analyst-provenance.md`; outline не лекция.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
