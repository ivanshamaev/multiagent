# 14 — Reviewer: quality judgment и separation от автора

Status: outline; lecture not written

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0014-review-authority.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[13](../../modules/module-13-qa-evidence/README.md)

## Теоретические outcomes

- Объяснить review authority, предпосылки и ограничения.
- Объяснить false approval, предпосылки и ограничения.
- Объяснить maintainability judgment, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `review authority`, `false approval`, `maintainability judgment`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Развести semantic QA и architecture/maintainability review.
- Объяснить право принять/отклонить изменение и запрет self-approval.
- Показать fresh read-only reviewer context и четыре retained mutations.
- Обсудить correlated blind spots: отдельная роль не гарантирует статистическую независимость.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: runtime/reviewer_workflow.py; STEP-0011; EXP-0004

- [runtime/reviewer_workflow.py](../../../runtime/reviewer_workflow.py)
- [plan/evidence/STEP-0011-reviewer-approval-gate.md](../../../plan/evidence/STEP-0011-reviewer-approval-gate.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Code Health: Google’s Internal Code Quality Efforts](https://testing.googleblog.com/2017/04/code-health-googles-internal-code.html) — Code health сверх бинарного test result.
- [Multi-Agents: What’s Actually Working](https://cognition.com/blog/multi-agents-working) — Дополнительный интеллектуальный review при сохранении single writer.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Будущий текст: `course/lectures/LECTURE-0014-review-authority.md`; outline не лекция.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
