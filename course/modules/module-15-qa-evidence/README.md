# 15 — QA: независимые проверки и принятие дефекта

Status: outline; lecture not written

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0015-qa-evidence.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[14](../../modules/module-14-data-engineer/README.md)

## Теоретические outcomes

- Объяснить QA independent probes, предпосылки и ограничения.
- Объяснить mutation detection, предпосылки и ограничения.
- Объяснить accepted defect evidence, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `QA independent probes`, `mutation detection`, `accepted defect evidence`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Развести public validator success и независимую semantic probe.
- Объяснить mutation/false pass и authority QA сообщать defect, не исправлять candidate.
- Разобрать code-owned immutable SQL probes и fresh assessment.
- Применить один QA mutation как case; механическое rework routing и статистику вынести владельцам.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: runtime/qa_workflow.py; tests/fixtures/qa_mutants/; STEP-0010; EXP-0003

- [runtime/qa_workflow.py](../../../runtime/qa_workflow.py)
- [plan/evidence/STEP-0010-qa-quality-loop.md](../../../plan/evidence/STEP-0010-qa-quality-loop.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Why data testing is essential for analytics engineering](https://www.getdbt.com/blog/data-testing) — Data assertions и доверие к результату.
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — Несколько проверяющих аспектов результата.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Будущий текст: `course/lectures/LECTURE-0015-qa-evidence.md`; outline не лекция.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
