# 05 — MAF: executors, edges и runtime графа

Status: outline; lecture not written

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0005-maf-executors.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[02](../../modules/module-02-contracts/README.md), [04](../../modules/module-04-state-memory/README.md)

## Теоретические outcomes

- Объяснить executor semantics, предпосылки и ограничения.
- Объяснить edge message delivery, предпосылки и ограничения.
- Объяснить runtime graph signature, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `executor semantics`, `edge message delivery`, `runtime graph signature`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Разобрать executor как runtime unit и edge как путь доставки, отдельно от бизнес-перехода.
- Объяснить graph state/messages и границу adapter/domain reducer.
- Показать typed JSON boundary в six-role graph и значение graph signature.
- Сравнить framework abstractions без рейтинга stars, неподтверждённых API обещаний и SDK tutorial.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: runtime/role_pipeline.py; STEP-0019

- [runtime/role_pipeline.py](../../../runtime/role_pipeline.py)
- [plan/evidence/STEP-0019-checkpointable-role-pipeline.md](../../../plan/evidence/STEP-0019-checkpointable-role-pipeline.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Introducing Microsoft Agent Framework: The Open-Source Engine for Agentic AI Apps](https://devblogs.microsoft.com/foundry/introducing-microsoft-agent-framework-the-open-source-engine-for-agentic-ai-apps/) — Agent/workflow runtime как разные orchestration возможности.
- [LangGraph: Multi-Agent Workflows](https://www.langchain.com/blog/langgraph-multi-agent-workflows) — Graph representation, без переобъяснения supervisor policy.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Будущий текст: `course/lectures/LECTURE-0005-maf-executors.md`; outline не лекция.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
