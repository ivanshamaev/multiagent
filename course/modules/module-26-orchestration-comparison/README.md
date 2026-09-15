# 26 — Workflow vs agent-orchestrator: сценарии, trade-offs и гибрид

Status: outline; lecture not written

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0026-orchestration-comparison.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[15](../../modules/module-15-strict-workflow/README.md), [16](../../modules/module-16-agent-orchestrator/README.md), [19](../../modules/module-19-security-authority/README.md), [21](../../modules/module-21-evaluation/README.md), [23](../../modules/module-23-cost-performance/README.md)

## Теоретические outcomes

- Объяснить scenario architecture selection, предпосылки и ограничения.
- Объяснить hybrid orchestration envelope, предпосылки и ограничения.
- Объяснить risk/adaptivity decision matrix, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `scenario architecture selection`, `hybrid orchestration envelope`, `risk/adaptivity decision matrix`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Сравнить ownership plan/routing/stopping, predictability, audit/replay, адаптивность, cost/latency и риски.
- Показать для каждого подхода преимущества/недостатки и cases, где он оправдан или избыточен.
- Разобрать минимум восемь data-engineering scenarios по единой rubric, включая alternative single agent/no agent.
- Описать hybrid: dynamic read investigation внутри static permission/quality/write gates; не считать любой orchestrator безграничным.
- Сопоставить Anthropic и Cognition без ложного универсального победителя; дать критерии выбора, а не vendor recommendation.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: Our workflow as implemented baseline; dynamic/hybrid variants explicitly hypothetical; ADR-0035

Нет execution anchors для этого теоретического варианта.

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — Архитектурная граница predefined vs model-directed flow.
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) — Применимость динамического исследования.
- [Don’t Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents) — Ограничения разделения зависимых действий.
- [Multi-Agents: What’s Actually Working](https://cognition.com/blog/multi-agents-working) — Managed intellectual parallelism при single writer.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Будущий текст: `course/lectures/LECTURE-0026-orchestration-comparison.md`; outline не лекция.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
