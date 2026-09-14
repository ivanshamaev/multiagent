# PRB-0047 — Tempo 2.x compaction fields were invalid in Tempo 3.0

Status: resolved

Date: 2026-09-14

## Symptom and reproduction

Первый `make observability-smoke` ожидал Tempo 60 секунд и завершился по timeout. Контейнер Tempo
сразу выходил с code 1: поля `ingester` и `compactor` отсутствовали в активном типе конфигурации.

## Cause

Tempo 3.0 удалил legacy top-level `ingester` и `compactor` blocks. Retention перемещён в
`backend_scheduler.provider.compaction.compaction` и `backend_worker.compaction`; первоначальная
конфигурация смешивала pinned 3.0 binary с 2.x schema.

## Fix and regression

В `observability/tempo.yaml` сохранён explicit `target: all`, удалены legacy blocks и одинаковая 72h
retention задана scheduler и worker. Regression gate запускает реальный pinned Tempo образ в
`make observability-smoke`, ожидает HTTP readiness и затем читает экспортированный trace.
