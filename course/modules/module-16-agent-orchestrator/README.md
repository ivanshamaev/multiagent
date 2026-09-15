# 16 — Agent-orchestrator: planning, delegation и replanning

Status: outline; lecture not written

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0016-agent-orchestrator.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[15](../../modules/module-15-strict-workflow/README.md)

## Теоретические outcomes

- Объяснить model-directed delegation, предпосылки и ограничения.
- Объяснить task/progress ledger, предпосылки и ограничения.
- Объяснить planner/executor separation, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `model-directed delegation`, `task/progress ledger`, `planner/executor separation`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Разобрать manager → bounded worker → synthesis → replanning и критерии достаточности результата.
- Объяснить task/progress ledgers, рабочую очередь, scope worker и завершение dynamic subtask.
- Развести dynamic routing, workers-as-tools, hierarchical teams и A2A transport.
- Сопоставить план модели с code-owned permission/approval shell; обозначить отсутствие реализации у нас.
- Показать research/schema investigation как мысленный пример, не как выполненный pipeline.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `not-implemented`. Исходный ракурс: External architecture only; ours remains code-owned workflow; ADR-0035

Нет execution anchors для этого теоретического варианта.

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Model-directed manager не реализован в нашем runtime.

## Статьи и переиспользуемые идеи

- [Magentic-One: A Generalist Multi-Agent System for Solving Complex Tasks](https://www.microsoft.com/en-us/research/articles/magentic-one-a-generalist-multi-agent-system-for-solving-complex-tasks/) — Task/progress ledgers и replanning.
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) — Делегирование исследовательских subtasks с явными boundaries.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Будущий текст: `course/lectures/LECTURE-0016-agent-orchestrator.md`; outline не лекция.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
