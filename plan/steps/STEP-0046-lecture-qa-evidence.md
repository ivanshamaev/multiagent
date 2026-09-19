# STEP-0046 — Phase L: лекция 15, QA и доказательство дефекта

Status: complete

Owner: Codex

Updated: 2026-09-18

## Цель и границы

Написать theory-only лекцию 15 о независимой QA-проверке после validator:
probe как дополнительный источник свидетельств, mutation как способ
обнаружить blind spot, typed defect evidence и пределы PASS. Пример —
Net Revenue `refund-date` mutation. Не повторять реализацию/repair DE (14),
reducer budget (06), review authority (16) и evaluation benchmark (21).

Новый per-lecture gate — **только текст**: полная редакторская вычитка,
проверка claims/источников, смысловая сверка Mermaid source и текстового
эквивалента. Не создавать скриншоты, не проводить browser/visual review,
не заявлять visual/AX PASS. Машинная сборка проверяет целостность Markdown/SVG,
но не визуальное качество.

## Порядок и критерии приёмки

- [x] Прочитать S18/S20 и сверить `runtime/qa.py`, `qa_workflow.py`,
  immutable probe, profile, mutation corpus, STEP-0010 и EXP-0003.
- [x] Написать лекцию с моделью validator → QA, условиями независимости,
  таблицей видов evidence, диаграммой, `refund-date` контрпримером,
  ограничениями и 3–5 вопросами.
- [x] Выполнить отдельные editorial, technical и recheck passes по всему
  тексту; сохранить schema-v2 content receipt с source anchors и hashes.
- [x] Проверить Markdown/links и статическую candidate/publication сборку,
  сохранить text-only publication receipt без screenshots/visual fields.
- [x] Обновить todo/manifest/index/evidence; две сборки побайтно совпадают,
  `make check`, plan/course governance и `git diff --check` проходят.

## Риски

Публичный validator PASS ограничен своими проверками; QA PASS ограничен
заданным probe и текущим состоянием данных. Мутация `weakened-test` не
обязательно различима одним SQL-probe: инспекция теста тоже существенна.
Исторический sample 5/5 — не свежая оценка качества модели и не гарантия
безошибочной QA. Отдельная роль не даёт статистической независимости сама
по себе. Исторический live PM завершился BLOCKED, не fully-live READY.

## Work log

2026-09-18: план создан до авторства лекции и изменений publication metadata.
2026-09-18: лекция написана и опубликована; separate text-only review receipts
сохранены. Candidate и две production-сборки прошли, последние побайтно
совпали. `make check`: 532 passed, exit 0. См. `plan/evidence/STEP-0046-lecture-qa-evidence.md`.
