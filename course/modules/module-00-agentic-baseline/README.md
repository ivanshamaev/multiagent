# 00 — Агентная система: agency, reasoning и среда

Status: companion outline page; lecture text published separately through STEP-0030 gate

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0000-agentic-baseline.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

Нет.

## Теоретические outcomes

- Объяснить agency, предпосылки и ограничения.
- Объяснить agent loop, предпосылки и ограничения.
- Объяснить reasoning/action/observation, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `agency`, `agent loop`, `reasoning/action/observation`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Развести LLM-вызов, tool-using agent и multi-agent system, не определяя топологии управления.
- Показать observation как внешний сигнал; отделить план/объяснение от фактического outcome.
- Объяснить ограниченную рациональность и критерии остановки одного agent loop.
- Использовать минимальную схему модели и среды; не публиковать private reasoning.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: runtime/agent_runtime.py; STEP-0007

- [runtime/agent_runtime.py](../../../runtime/agent_runtime.py)
- [plan/evidence/STEP-0007-local-agent-runtime.md](../../../plan/evidence/STEP-0007-local-agent-runtime.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) — Связь действия с наблюдением, без копирования reasoning traces.
- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — Уровень автономии, без обзора всех workflow patterns.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Текст подготовлен отдельно: `course/lectures/LECTURE-0000-agentic-baseline.md`; эта страница остаётся outline, не опубликованной лекцией.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
