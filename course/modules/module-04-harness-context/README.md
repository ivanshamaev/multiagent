# 04 — Harness и инженерия контекста одного вызова

Status: outline; lecture not written

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0004-harness-context.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[3](../../modules/module-03-contracts/README.md)

## Теоретические outcomes

- Объяснить per-turn context selection, предпосылки и ограничения.
- Объяснить model-provider abstraction, предпосылки и ограничения.
- Объяснить structured response boundary, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `per-turn context selection`, `model-provider abstraction`, `structured response boundary`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Разделить harness loop, transport adapter и domain logic.
- Объяснить selection/compaction и token-relevant information на уровне текущего вызова.
- Сопоставить prompt, retrieved material и tool results без повторения storage consistency.
- Разобрать structured response и error handling; persistent recovery и экономику отправить владельцам.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: runtime/context.py; runtime/model_provider.py; STEP-0007

- [runtime/context.py](../../../runtime/context.py)
- [runtime/model_provider.py](../../../runtime/model_provider.py)
- [plan/evidence/STEP-0007-local-agent-runtime.md](../../../plan/evidence/STEP-0007-local-agent-runtime.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Отбор ограниченного полезного контекста.
- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — Progressive disclosure знаний, не реализация runtime skills.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Будущий текст: `course/lectures/LECTURE-0004-harness-context.md`; outline не лекция.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
