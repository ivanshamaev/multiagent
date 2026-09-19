# 23 — Cost/performance: budgets, critical path и эффективность

Status: lecture written; text-only reviewed

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0023-cost-performance.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[21](../../modules/module-21-evaluation/README.md), [07](../../modules/module-07-agent-orchestrator/README.md)

## Теоретические outcomes

- Объяснить budget allocation, предпосылки и ограничения.
- Объяснить critical-path cost trade-off, предпосылки и ограничения.
- Объяснить tool context overhead, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `budget allocation`, `critical-path cost trade-off`, `tool context overhead`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Дать модель total cost с retries/manager/synthesis/tool output, не только price per token.
- Разобрать parallel read benefits vs synchronization/write conflict и rate constraints.
- Объяснить cost-first capability gate и контроль качества при уменьшении бюджета.
- Показать dated GateLLM accounting; не обещать актуальные цены, caching или model router, которых нет.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: runtime/model_provider.py; STEP-0009 sample; EXP-0001

- [runtime/model_provider.py](../../../runtime/model_provider.py)
- [plan/evidence/STEP-0009-autonomous-data-engineer.md](../../../plan/evidence/STEP-0009-autonomous-data-engineer.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Code execution with MCP: Building more efficient agents](https://www.anthropic.com/engineering/code-execution-with-mcp) — Tool definitions/results как расход контекста.
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) — Экономическая граница multi-agent research.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Текст: [course/lectures/LECTURE-0023-cost-performance.md](../../lectures/LECTURE-0023-cost-performance.md).
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams проходят text-only source review
и машинную сборку без скриншотов или visual/AX/browser PASS.
