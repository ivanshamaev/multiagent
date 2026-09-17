# 09 — MCP как интерфейс, а не политика координации

Status: reviewed; publication gate complete

Track: core

[Лекция](../../lectures/LECTURE-0009-mcp-interface.md) · [Todo-план](../../../plan/steps/lections/LECTURE-0009-mcp-interface.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[08](../../modules/module-08-isolation/README.md), [03](../../modules/module-03-harness-context/README.md)

## Теоретические outcomes

- Объяснить MCP host/client/server, предпосылки и ограничения.
- Объяснить protocol capability negotiation, предпосылки и ограничения.
- Объяснить tool interface ergonomics, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `MCP host/client/server`, `protocol capability negotiation`, `tool interface ergonomics`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Объяснить роли host/client/server, transport и negotiated capabilities.
- Развести tool call, agent delegation и workflow transition.
- Описать tool names/parameters/results как semantic interface, не произвольный API pass-through.
- Разграничить protocol guarantees и repository-owned authorization; OAuth details сверять отдельно.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: runtime/tools/mcp_gateway.py; runtime/tools/mcp_stdio.py; STEP-0008

- [runtime/tools/mcp_gateway.py](../../../runtime/tools/mcp_gateway.py)
- [runtime/tools/mcp_stdio.py](../../../runtime/tools/mcp_stdio.py)
- [plan/evidence/STEP-0008-tool-policy-layer.md](../../../plan/evidence/STEP-0008-tool-policy-layer.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol) — Унифицированный интерфейс подключения данных.
- [Writing effective tools for agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — Tool ergonomics и понятные boundaries.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Текст: `course/lectures/LECTURE-0009-mcp-interface.md`; publication gate завершён.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
