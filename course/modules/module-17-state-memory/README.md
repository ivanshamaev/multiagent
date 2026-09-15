# 17 — Context, durable state, artifacts и knowledge

Status: outline; lecture not written

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0017-state-memory.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[4](../../modules/module-04-harness-context/README.md)

## Теоретические outcomes

- Объяснить state lifecycle, предпосылки и ограничения.
- Объяснить artifact visibility, предпосылки и ограничения.
- Объяснить durable vs ephemeral knowledge, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `state lifecycle`, `artifact visibility`, `durable vs ephemeral knowledge`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Разделить conversation context, workflow snapshot, task artifact и long-term knowledge.
- Объяснить lifetime/visibility/consistency и потерю информации при summarization.
- Сопоставить shared scratchpad с accepted artifact handoff без повторения schemas.
- Показать текущее context/state; long-term memory описать как альтернативу, не как установленный layer.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: runtime/context.py; contracts/artifacts.py; STEP-0019

- [runtime/context.py](../../../runtime/context.py)
- [contracts/artifacts.py](../../../contracts/artifacts.py)
- [plan/evidence/STEP-0019-checkpointable-role-pipeline.md](../../../plan/evidence/STEP-0019-checkpointable-role-pipeline.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.
- Long-term semantic memory не реализована.

## Статьи и переиспользуемые идеи

- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Compaction/structured notes как способы работы с контекстом.
- [Don’t Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents) — Контекст и согласованность implicit decisions.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Будущий текст: `course/lectures/LECTURE-0017-state-memory.md`; outline не лекция.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
