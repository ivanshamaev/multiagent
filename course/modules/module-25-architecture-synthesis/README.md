# 25 — Итоговый синтез: наш мультиагент как система

Status: lecture written; text-only reviewed

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0025-architecture-synthesis.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[24](../../modules/module-24-orchestration-comparison/README.md), [22](../../modules/module-22-failure-taxonomy/README.md), [13](../../modules/module-13-pm-specification/README.md), [14](../../modules/module-14-data-engineer/README.md)

## Теоретические outcomes

- Объяснить integrated architecture rationale, предпосылки и ограничения.
- Объяснить evidence-bounded system claims, предпосылки и ограничения.
- Объяснить cross-layer change impact, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `integrated architecture rationale`, `evidence-bounded system claims`, `cross-layer change impact`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Собрать существующие concepts в четыре слоя и один Net Revenue architecture walkthrough.
- Проследить known facts → requirements → implementation → independent quality → terminal outcome.
- Отдельно показать доказанное offline/live, NEEDS_USER и оставшиеся integration gaps.
- Сформулировать последствия смены одного layer, не повторяя определения/сравнение из 24.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: STEP-0010/0013/0020/0024; ADR/PRB/EXP anchors

- [plan/evidence/STEP-0010-qa-quality-loop.md](../../../plan/evidence/STEP-0010-qa-quality-loop.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Multi-Agents: What’s Actually Working](https://cognition.com/blog/multi-agents-working) — Согласованность действий при расширении интеллектуальной команды.
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — Прогресс и evidence завершения как итоговое чтение.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Текст: [course/lectures/LECTURE-0025-architecture-synthesis.md](../../lectures/LECTURE-0025-architecture-synthesis.md).
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams проходят text-only source review
и машинную сборку без скриншотов или visual/AX/browser PASS.
