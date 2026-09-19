# 17 — Recovery: checkpoints, receipts и пределы exactly-once

Status: lecture written; text-only reviewed

Track: core

[Лекция](../../lectures/LECTURE-0017-recovery-idempotency.md) · [Todo-план](../../../plan/steps/lections/LECTURE-0017-recovery-idempotency.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[06](../../modules/module-06-strict-workflow/README.md), [04](../../modules/module-04-state-memory/README.md)

## Теоретические outcomes

- Объяснить checkpoint commit boundary, предпосылки и ограничения.
- Объяснить operation idempotency, предпосылки и ограничения.
- Объяснить receipt crash windows, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `checkpoint commit boundary`, `operation idempotency`, `receipt crash windows`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Разобрать kill до/после role receipt и durable checkpoint; разные окна повторного исполнения.
- Дать определения at-most/at-least/exactly-once относительно наблюдаемого эффекта.
- Объяснить request IDs, reconciliation и почему checkpoint не гарантирует exactly-once внешнего side effect.
- Показать staged 0600 publication и receipt-backed restart; не превращать в fault-injection lab.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: runtime/checkpoints.py; runtime/role_receipts.py; STEP-0018/0024; PRB-0052

- [runtime/checkpoints.py](../../../runtime/checkpoints.py)
- [runtime/role_receipts.py](../../../runtime/role_receipts.py)
- [plan/evidence/STEP-0018-checkpoint-resume-crash-recovery.md](../../../plan/evidence/STEP-0018-checkpoint-resume-crash-recovery.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) — Idempotent request identity и повторные эффекты.
- [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents) — Durability session и исполняемая среда как разные lifecycles.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Текст: `course/lectures/LECTURE-0017-recovery-idempotency.md`.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams проходят text-only source review
и машинную сборку без скриншотов или visual/AX/browser PASS.
