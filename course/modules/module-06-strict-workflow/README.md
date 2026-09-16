# 06 — Жёсткий workflow: reducer, branching и convergence

Status: outline; lecture not written

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0006-strict-workflow.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[05](../../modules/module-05-maf-executors/README.md)

## Теоретические outcomes

- Объяснить code-owned transition policy, предпосылки и ограничения.
- Объяснить terminal convergence, предпосылки и ограничения.
- Объяснить bounded rework routing, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `code-owned transition policy`, `terminal convergence`, `bounded rework routing`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Дать модель workflow transition relation и разделить safety/liveness.
- Объяснить fixed graph с branching, parallel edges и bounded loops: жёсткий не значит только linear DAG.
- Разобрать reducer-owned BLOCKED/FAILED/DONE, acceptance gates и rework invalidation.
- Показать six-role code path; model reasoning внутри стадии не передаёт LLM право менять transitions.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: runtime/role_pipeline.py; orchestrator/transitions.py; STEP-0020

- [runtime/role_pipeline.py](../../../runtime/role_pipeline.py)
- [orchestrator/transitions.py](../../../orchestrator/transitions.py)
- [plan/evidence/STEP-0020-branching-rework-idempotency.md](../../../plan/evidence/STEP-0020-branching-rework-idempotency.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — Предопределённые пути управления.
- [LangGraph: Multi-Agent Workflows](https://www.langchain.com/blog/langgraph-multi-agent-workflows) — Graph и возможные cycles как runtime model.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Будущий текст: `course/lectures/LECTURE-0006-strict-workflow.md`; outline не лекция.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
