# STEP-0036 — Phase L: лекция 05, MAF executors и edges

Status: complete

Owner: Codex

Updated: 2026-09-17

## Goal и boundaries

После завершённого STEP-0035 последовательно написать и опубликовать
theory-only лекцию 05. Её область — executor как единица исполнения,
edge как доставка сообщения, typed boundary и graph signature. Не повторять
схемы контрактов (02), lifetime состояния (04), бизнес-transition/rework (06)
или crash semantics (17). Использовать текущий six-role MAF graph как
`offline-proven` пример, не как доказательство live качества модели.

Разрешены текст/TODO/module 05, manifest/receipts и индексы/step/evidence.
Runtime, platform, общие hashed inputs и опубликованные тексты не менять.
Нет labs, Docker mutations, paid model calls или SDK tutorial.

## Acceptance и проверки

- [x] Перечитать S06/S05, code/tests, STEP-0019, prerequisites и соседние owners.
- [x] Написать definitions, причинность, ограничения, counterexample, Mermaid,
  реальный typed boundary, 3–5 вопросов и переход к 06.
- [x] Отдельные authoring/editorial/claim verification/recheck; актуальный
  content receipt со scope, source anchors и skill fingerprints.
- [x] Candidate render и actual browser/visual проверки на desktop/mobile,
  light/dark, no-JS, keyboard, print, AX, CSP/subpath/links; actual AT — отдельно.
- [x] Publication receipt, reviewed-only manifest, targeted tests,
  две одинаковые обычные сборки, `make check`, governance, evidence.

## Риски

Не приравнивать edge к business decision или graph signature к гарантии
семантической совместимости. MAF API описывать только в подтверждённой версии
кода; исторический STEP-0019 не доказывает текущий live run. Shared
framework абстракция не делает разные платформы взаимозаменяемыми.

## Work log

2026-09-17: план создан после закрытия STEP-0035, до авторства лекции 05.

2026-09-17: лекция 05 опубликована после seven-claim content review и actual
browser/visual gate. Targeted 11 PASS; `make check` 531 PASS; обычные сборки
90 files/10 diagrams побайтово совпали. Preview 8099 HTTP 200. Actual AT
остаётся непроверенным. [Evidence](../evidence/STEP-0036-lecture-maf-executors.md).
