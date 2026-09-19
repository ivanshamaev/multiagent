# STEP-0054 — Phase L: лекция 23, Cost/performance

Status: complete

Owner: Codex

Updated: 2026-09-19

## Цель и границы

Написать theory-only лекцию 23 о полной стоимости agentic execution,
распределении budgets, critical path и tool-context overhead. Показать,
почему price per token не равен cost per accepted outcome, а parallelism
снижает latency только при независимых ветвях и доступных shared resources.
Разобрать cost-first capability gate и обязательную повторную evaluation
после уменьшения бюджета. Не повторять harness/context (03), manager model
(07), evaluation statistics (21), failure taxonomy (22) и архитектурную
матрицу выбора (24). Не запускать paid models и не запрашивать актуальные
GateLLM цены.

Затрагиваемые пути: `course/lectures/`, module23/manifest/reviews/index,
`plan/steps/lections/`, `plan/evidence/`, course/plan status records.

## Порядок и критерии приёмки

- [x] Проверить Anthropic S26/S02, текущие budget/accounting contracts и
  датированные EXP-0001/STEP-0009 measurements.
- [x] Написать глубокую лекцию с cost model, latency/critical-path model,
  budget hierarchy, parallel-read/write-contention analysis, контрпримером,
  Mermaid-диаграммой и текстовым эквивалентом.
- [x] Не выдавать catalog price за total cost, provider usage за полный
  resource accounting, parallel branches — за бесплатное ускорение, а
  historical ₽/latency — за актуальный price/SLO.
- [x] Выполнить отдельные editorial, technical, diagram semantics и recheck
  passes; сохранить schema-v2 content receipt с source anchors/hashes.
- [x] Проверить Markdown/links и candidate/static build; сохранить text-only
  publication receipt без screenshots/browser/visual/AX review.
- [x] Обновить todo/manifest/index/evidence; две production-сборки побайтно
  совпадают, `make check`, governance и `git diff --check` проходят.

## Риски и ограничения

Token price зависит от модели/provider и времени; в лекции допустимы только
датированные measurements. Provider usage может не учитывать probe,
retries, tool runtime, infrastructure и человеческую проверку. Critical
path нельзя вычислять как сумму всех branch durations; cost, latency и
quality образуют разные ограничения. Dynamic manager/router/caching в
репозитории не реализованы и не должны появиться как текущие возможности.

## Work log

2026-09-19: план создан до авторства лекции; начата сверка источников,
accounting code и historical measurements.
2026-09-19: лекция опубликована, same-author content/publication receipts
сохранены; две production-сборки совпали; `make check` — 532 passed.
[Evidence](../evidence/STEP-0054-lecture-cost-performance.md).
