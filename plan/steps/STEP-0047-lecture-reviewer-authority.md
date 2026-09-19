# STEP-0047 — Phase L: лекция 16, Reviewer и право одобрения

Status: complete

Owner: Codex

Updated: 2026-09-18

## Цель и границы

Написать theory-only лекцию 16: отличие semantic QA от judgment о качестве изменения,
authority Reviewer, запрет self-approval, false approval и пределы разделения ролей.
Сквозной пример — Net Revenue и четыре retained reviewer mutations. Не повторять
теорию QA (15), separation of duties (01), evaluation benchmark (21) или
rework mechanics (06). Data Platform/runtime и paid models не менять.

Затрагиваемые пути: `course/lectures/`, module16/manifest/reviews/index,
`plan/steps/lections/`, `plan/evidence/`, course/plan status records.

## Порядок и критерии приёмки

- [x] Сверить S19/S04, reviewer code/profile/contract, STEP-0011, EXP-0004
  и four-mutant manifest; ограничить historical/live claims.
- [x] Написать лекцию с причинным разбором approval, maintainability,
  контрпримером, Mermaid-диаграммой, текстовым эквивалентом и 3–5 вопросами.
- [x] Выполнить отдельные editorial, technical, diagram semantics и recheck
  passes; сохранить schema-v2 content receipt с source anchors и hashes.
- [x] Проверить Markdown/links и candidate/static publication build; сохранить
  text-only publication receipt. Без screenshots, browser/visual/AX review.
- [x] Обновить todo/manifest/index/evidence; две сборки побайтно совпадают,
  `make check`, plan/course governance и `git diff --check` проходят.

## Риски и полномочия

Отдельная роль не гарантирует независимое суждение. `APPROVE` локального
Reviewer — accepted переход workflow, не production deploy/merge. Исторический
mutation corpus не является оценкой вероятности false approval. Разрешены
только локальные документы и неплатная проверка; approvals не требуются.

## Work log

2026-09-18: план создан до авторства лекции.
2026-09-18: лекция написана и опубликована; text-only content/publication
receipts сохранены. Candidate и две production-сборки прошли, последние
побайтно совпали. `make check`: 532 passed, exit 0; итоговые governance
и `git diff --check`: exit 0. См. `plan/evidence/STEP-0047-lecture-reviewer-authority.md`.
