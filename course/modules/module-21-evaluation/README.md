# 21 — Evaluation: outcome, baseline и статистическая неопределённость

Status: outline; lecture not written

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0021-evaluation.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[13](../../modules/module-13-qa-evidence/README.md), [14](../../modules/module-14-review-authority/README.md), [20](../../modules/module-20-observability/README.md)

## Теоретические outcomes

- Объяснить task/trial distinction, предпосылки и ограничения.
- Объяснить quality vs invariant evaluation, предпосылки и ограничения.
- Объяснить baseline comparison uncertainty, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `task/trial distinction`, `quality vs invariant evaluation`, `baseline comparison uncertainty`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Определить task/trial/grader/outcome и единицу измерения reliability.
- Развести offline invariants, dated live model rates и статистическое сравнение fresh samples.
- Разобрать false pass/false approval, выборку/доверие, contamination и ограничения малого N.
- Показать 17×3 harness и DE historical sample; путь dynamic manager оценивать не по идентичности trajectory.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: evals/phase_k/; STEP-0024; STEP-0009 sample

- [plan/evidence/STEP-0024-phase-k-evaluation-benchmark.md](../../../plan/evidence/STEP-0024-phase-k-evaluation-benchmark.md)
- [plan/evidence/STEP-0009-autonomous-data-engineer.md](../../../plan/evidence/STEP-0009-autonomous-data-engineer.md)

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — Outcome-oriented multi-turn evaluation.
- [Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise) — Контроль инфраструктурных переменных эксперимента.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Будущий текст: `course/lectures/LECTURE-0021-evaluation.md`; outline не лекция.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
