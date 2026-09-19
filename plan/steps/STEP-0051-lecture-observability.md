# STEP-0051 — Phase L: лекция 20, Observability

Status: complete

Owner: Codex

Updated: 2026-09-19

## Цель и границы

Написать theory-only лекцию 20 о trace causality, propagation через restart,
кардинальности telemetry и компромиссах sampling/retention. Развести trace,
event log, metrics и artifact provenance; не выдавать trace за private model
reasoning, semantic correctness или audit proof. Иллюстрировать материал
content-free OpenTelemetry chain и локальным Collector/Tempo/Prometheus/
Grafana, не переобъясняя recovery (17), evaluation (21) и failure taxonomy
(22). Не менять runtime/Data Platform и не запускать paid models.

Затрагиваемые пути: `course/lectures/`, module20/manifest/reviews/index,
`plan/steps/lections/`, `plan/evidence/`, course/plan status records.

## Порядок и критерии приёмки

- [x] Проверить Dapper S29, Managed Agents S27 и актуальные OpenTelemetry
  определения; сверить telemetry code/config/tests и STEP-0021/0023.
- [x] Написать глубокую лекцию: signal taxonomy, span hierarchy/carrier,
  content-free policy, cardinality, tail sampling/retention, counterexample
  и Mermaid-диаграмма с текстовым эквивалентом.
- [x] Выполнить отдельные editorial, technical, diagram semantics и recheck
  passes; сохранить schema-v2 content receipt с source anchors/hashes.
- [x] Проверить Markdown/links и candidate/static build; сохранить text-only
  publication receipt без screenshots/browser/visual/AX review.
- [x] Обновить todo/manifest/index/evidence; две production-сборки побайтно
  совпадают, `make check`, governance и `git diff --check` проходят.

## Риски и ограничения

Сохранённый parent span восстанавливает причинную связь, но не исполнение.
Sampling создаёт наблюдательную потерю; метрики из sampled spans не обязаны
описывать полную популяцию. Хеш фиксирует ссылочную identity, не истинность
или конфиденциальность исходного значения. Датированный single-host smoke
не доказывает HA, production retention или полноту trace.

## Work log

2026-09-19: план создан до авторства лекции.
2026-09-19: лекция опубликована, same-author content/publication receipts
сохранены; две production-сборки совпали; `make check` — 532 passed.
[Evidence](../evidence/STEP-0051-lecture-observability.md).
