# STEP-0053 — Phase L: лекция 22, Failure modes

Status: complete

Owner: Codex

Updated: 2026-09-19

## Цель и границы

Написать theory-only лекцию 22 о причинах отказов, их распространении и
retry amplification. Развести observable symptom и root cause, построить
taxonomy infrastructure/tool/workflow/reasoning/policy failures, показать
common-mode correlation, false completion и stale-state propagation.
Сопоставить ошибочную ветку code-owned workflow с ошибочным replan
теоретического agent-orchestrator. Recovery protocol оставить лекции 17,
eval metrics — 21, cost model — 23. Не менять runtime/Data Platform и не
запускать paid models.

Затрагиваемые пути: `course/lectures/`, module22/manifest/reviews/index,
`plan/steps/lections/`, `plan/evidence/`, course/plan status records.

## Порядок и критерии приёмки

- [x] Проверить AWS S13, Anthropic S21 и repository evidence
  PRB-0035/0051/0052 вместе с соответствующим кодом/тестами.
- [x] Написать глубокую лекцию: taxonomy, causal chain, common-mode
  failures, retry amplification, fixed graph vs manager, контрпример,
  Mermaid-диаграмма и текстовый эквивалент.
- [x] Не выдавать симптом за причину, коррелированные повторы — за
  независимые trials, backoff — за permission/reasoning repair, а
  историческое исправление — за отсутствие класса дефектов.
- [x] Выполнить отдельные editorial, technical, diagram semantics и recheck
  passes; сохранить schema-v2 content receipt с source anchors/hashes.
- [x] Проверить Markdown/links и candidate/static build; сохранить text-only
  publication receipt без screenshots/browser/visual/AX review.
- [x] Обновить todo/manifest/index/evidence; две production-сборки побайтно
  совпадают, `make check`, governance и `git diff --check` проходят.

## Риски и ограничения

Один наблюдаемый `timeout` может возникнуть из model, tool, network,
scheduler или budget причин. Retry без классификации способен повторить
необратимый effect или синхронизировать нагрузку. Общий oracle/fixture
создаёт коррелированные PASS/FAIL и завышает видимую независимость.
Manager runtime в репозитории не реализован: его ошибочный replan —
теоретический сценарий, а не execution evidence.

## Work log

2026-09-19: план создан до авторства лекции; начата сверка источников,
problem records и текущих regression boundaries.
2026-09-19: лекция опубликована, same-author content/publication receipts
сохранены; две production-сборки совпали; `make check` — 532 passed.
[Evidence](../evidence/STEP-0053-lecture-failure-taxonomy.md).
