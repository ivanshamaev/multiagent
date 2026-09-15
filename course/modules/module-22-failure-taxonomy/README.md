# 22 — Failure modes: причины, propagation и retry amplification

Status: outline; lecture not written

Track: core

[Todo-план](../../../plan/steps/lections/LECTURE-0022-failure-taxonomy.md) · [Manifest](../../manifest.json) · [Технические требования](../../technical-requirements.md)

## Место и prerequisites

[21](../../modules/module-21-evaluation/README.md)

## Теоретические outcomes

- Объяснить failure root-cause taxonomy, предпосылки и ограничения.
- Объяснить retry amplification, предпосылки и ограничения.
- Объяснить shared-fixture correlation, предпосылки и ограничения.

## Уникальная область и границы

Primary concepts: `failure root-cause taxonomy`, `retry amplification`, `shared-fixture correlation`.
Определения соседних тем не повторять: [карта владельцев](../../../plan/steps/lections/README.md).

## План объяснения

- Развести infrastructure/tool/workflow/reasoning/policy failures и observational symptoms.
- Объяснить retry storm, false completion, stale state и propagation через handoffs.
- Разобрать retained PRB-0035/0051/0052, отделяя причина/исправление/verification.
- Сравнить ошибочную ветку fixed graph и ошибочный replan; не переопределять recovery protocol или eval metrics.

Интуиция → предпосылки → причинность → контрпример → синтез, 3–5 вопросов и переход.
Нет student coding tasks или обязательных запусков.

## Иллюстрация нашей системой и provenance

Implementation boundary: `offline-proven`. Исходный ракурс: plan/problems/PRB-0035/0051/0052; associated evidence

Нет execution anchors для этого теоретического варианта.

Offline/code evidence ограничено своей областью. Proposed manager/hybrid не execution result.

## Known gaps

- Code/offline evidence не доказывает fully-live six-role READY/autonomous merge.

## Статьи и переиспользуемые идеи

- [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) — Jitter против синхронизированных retries.
- [Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise) — Infrastructure noise как источник ложных выводов.

Перечитать перед авторством; пересказать своими словами с attribution.
[Source caveats](../../../plan/steps/lections/SOURCES.md) обязательны.

## Авторство и проверка

Будущий текст: `course/lectures/LECTURE-0022-failure-taxonomy.md`; outline не лекция.
[Editorial guidelines](../../editorial-guidelines.md), [lecture template](../../templates/lecture.md),
[review schema](../../templates/review.json) требуют вычитку, technical verification и recheck.
Missing/stale receipt запрещает reviewed; diagrams требуют actual render/visual gate.
