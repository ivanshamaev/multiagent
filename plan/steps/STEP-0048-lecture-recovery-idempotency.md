# STEP-0048 — Phase L: лекция 17, recovery и idempotency

Status: complete

Owner: Codex

Updated: 2026-09-18

## Цель и границы

Написать theory-only лекцию 17 о checkpoint commit boundary, role receipt
crash windows, operation identity и различии at-most/at-least/exactly-once
для наблюдаемого эффекта. Пример — restart role pipeline, без fault-injection
lab. Не повторять state lifecycle (04), workflow routing (06), Airflow
операции (18) и failure taxonomy (22). Runtime/Data Platform и paid models
не менять.

Затрагиваемые пути: `course/lectures/`, module17/manifest/reviews/index,
`plan/steps/lections/`, `plan/evidence/`, course/plan status records.

## Порядок и критерии приёмки

- [x] Сверить S12/S27, `runtime/checkpoints.py`, `runtime/role_receipts.py`,
  role pipeline recovery, STEP-0018/0024, PRB-0052 и tests; точно отделить
  доказанное от предложения.
- [x] Написать лекцию с временной моделью сбоев, таблицей гарантий,
  контрпримером, Mermaid-диаграммой и текстовым эквивалентом, 3–5 вопросами.
- [x] Выполнить отдельные editorial, technical, diagram semantics и recheck
  passes; сохранить schema-v2 content receipt с source anchors и hashes.
- [x] Проверить Markdown/links, candidate/static publication build; сохранить
  text-only publication receipt без screenshots/browser/visual/AX review.
- [x] Обновить todo/manifest/index/evidence; две production-сборки побайтно
  совпадают, `make check`, governance и `git diff --check` проходят.

## Риски и полномочия

Checkpoint предотвращает повтор committed superstep, но не даёт exactly-once
для внешнего side effect внутри незавершённой роли. Receipt фиксирует
принятый результат, а не отменяет неопределённость после tool timeout.
Разрешены локальные документы и неплатные проверки; approvals не требуются.

## Work log

2026-09-18: план создан до авторства лекции.
2026-09-18: лекция опубликована; text-only content/publication receipts
сохранены. Candidate и две production-сборки прошли, последние побайтно
совпали. `make check`: 532 passed, exit 0; итоговые governance и
`git diff --check`: exit 0. Исправлен cross-reference outline 18.
См. `plan/evidence/STEP-0048-lecture-recovery-idempotency.md`.
