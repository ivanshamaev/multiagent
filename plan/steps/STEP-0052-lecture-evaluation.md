# STEP-0052 — Phase L: лекция 21, Evaluation

Status: complete

Owner: Codex

Updated: 2026-09-19

## Цель и границы

Написать theory-only лекцию 21 об evaluation как измерительной системе:
task/trial/grader/outcome, единицы надёжности, baseline и неопределённость.
Развести offline regression invariants, датированные live-прогоны модели и
статистическое сравнение свежих выборок. Показать false pass/false approval,
contamination и ограничения малого N на Phase K `17 × 3` и исторической
выборке Data Engineer. Не повторять обязанности QA (15), Reviewer (16),
observability (20), failure taxonomy (22) и cost/performance (23). Не менять
runtime/Data Platform и не запускать paid models.

Затрагиваемые пути: `course/lectures/`, module21/manifest/reviews/index,
`plan/steps/lections/`, `plan/evidence/`, course/plan status records.

## Порядок и критерии приёмки

- [x] Проверить Anthropic S20/S21 и repository code/evidence Phase K/STEP-0009.
- [x] Написать глубокую лекцию с формальной рамкой измерения, таблицей,
  контрпримером, Mermaid-диаграммой и текстовым эквивалентом.
- [x] Явно отделить 51 повтор исполнения фиксированных кейсов от 51
  независимой semantic tasks и policy threshold от измеренного comparator.
- [x] Выполнить отдельные editorial, technical, diagram semantics и recheck
  passes; сохранить schema-v2 content receipt с source anchors/hashes.
- [x] Проверить Markdown/links и candidate/static build; сохранить text-only
  publication receipt без screenshots/browser/visual/AX review.
- [x] Обновить todo/manifest/index/evidence; две production-сборки побайтно
  совпадают, `make check`, governance и `git diff --check` проходят.

## Риски и ограничения

`51/51 PASS` доказывает повторяемость проверяемых offline-инвариантов в
зафиксированном окружении, но не качество LLM. Исторические `7/10` — точечная
оценка одной датированной конфигурации с высокой неопределённостью, а не
вечная характеристика модели. `baseline.json` задаёт порог приёмки и не
является статистической контрольной группой. Повторы общего fixture могут
иметь коррелированные ошибки; изменение grader делает результаты
несопоставимыми.

## Work log

2026-09-19: план создан до авторства лекции; начата сверка первичных
источников и репозиторных evidence.
2026-09-19: лекция опубликована, same-author content/publication receipts
сохранены; две production-сборки совпали; `make check` — 532 passed.
[Evidence](../evidence/STEP-0052-lecture-evaluation.md).
