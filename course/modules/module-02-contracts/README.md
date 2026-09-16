# 02 — Контракты, артефакты и границы доверия

Status: outline; lecture not written

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0002-contracts.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[01](../../modules/module-01-organization/README.md)

## Теоретические outcomes

- Объяснить artifact schema, предпосылки и ограничения.
- Объяснить contract invariants, предпосылки и ограничения.
- Объяснить cross-task binding, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `artifact schema`, `contract invariants`, `cross-task binding`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Дать строгую модель input/output contract: syntax validity не означает semantic correctness.
- Объяснить versioning, immutable artifacts и task/actor binding.
- Рассмотреть malformed payload, extra fields и ложное утверждение completion как разные нарушения.
- Показать TaskSpecification/ImplementationResult/Evidence без полного обзора workflow состояний.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: contracts/artifacts.py; STEP-0006; ADR-0014

- [contracts/artifacts.py](../../../contracts/artifacts.py)
- [plan/evidence/STEP-0006-contracts-state-machine.md](../../../plan/evidence/STEP-0006-contracts-state-machine.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Writing effective tools for agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — Ясные интерфейсы и границы параметров.
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — Разница заявленного ответа и outcome.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Текст написан и опубликован в STEP-0032: [лекция 02](../../lectures/LECTURE-0002-contracts.md).
Этот файл сохраняет planning outline; reader выбирает полный текст по manifest/receipts.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
