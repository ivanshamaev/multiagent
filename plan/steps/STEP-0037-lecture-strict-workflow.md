# STEP-0037 — Phase L: лекция 06, жёсткий workflow

Status: complete

Owner: Codex

Updated: 2026-09-17

## Goal и scope

После опубликованной 05 последовательно написать и опубликовать theory-only
лекцию 06. Primary owner: code-owned transition relation, safety/liveness,
terminal convergence и bounded rework. Показать branching/cycles без
приравнивания жёсткого workflow к линейному DAG. Наша система —
`orchestrator/transitions.py`, `runtime/role_pipeline.py` и датированный
STEP-0020, строго offline-proven.

Не пересказывать executor delivery (05), dynamic manager (07), crash/idempotency
(17) и архитектурный выбор (24). Не менять runtime/platform, common hashed inputs
или уже опубликованные тексты. Нет labs, paid model или Docker mutations.

## Acceptance и verification

- [x] Прочитать первичные S01/S05, code/tests и STEP-0020; уточнить временной scope.
- [x] Написать transition model, safety/liveness distinction, пример rework,
  контрпример, Mermaid, 3–5 вопросов и переход к 07.
- [x] Отдельные authoring/editorial/technical/recheck и content receipt.
- [x] Candidate SVG/HTML и actual browser+visual desktop/mobile/no-JS/keyboard/
  print/AX/CSP/links gate; записать неохваченный actual AT.
- [x] Publication receipt, reviewed manifest, targeted tests, две идентичные
  сборки, `make check`, evidence и доступный preview 8099.

## Risks

Не выдавать safety за полную liveness: bounded budget и terminal outcome дают
ограничение попыток, но зависший внешний вызов требует timeout enforcement.
Не изображать model-generated verdict как полномочие самому менять Stage.
STEP-0020 относится к версии v2; нынешний v3 сравнивается с кодом и тестами.

## Work log

2026-09-17: план создан после завершения STEP-0036, до авторства 06.

2026-09-17: лекция 06 опубликована после eight-claim content review,
browser/visual gate и семи просмотренных screenshots. Targeted workflow:
30 PASS; `make check`: 531 PASS. Две обычные сборки 92 files/11 diagrams
побайтово совпали; preview 8099 HTTP 200. Actual AT не тестировалось.
[Evidence](../evidence/STEP-0037-lecture-strict-workflow.md).
