# PRB-0049 — Persistent Prometheus series caused a false sampling timeout

Status: resolved

Date: 2026-09-14

## Symptom and reproduction

Первый post-fix live smoke прошёл, но следующий запуск с сохранённым Prometheus volume ожидал
увеличения `keep-errors` counter 60 секунд и завершился timeout, хотя новый trace появился в Tempo.

## Cause

Smoke прочитал последнее persisted значение sampling series сразу после `up=1`, до того как scrape
нового Collector пометил отсутствующую старую series stale. Новый Collector начал counter с единицы,
равной сохранённому значению, поэтому сравнение абсолютных значений не увидело увеличение.

## Fix and regression

Collector internal metrics endpoint опубликован только на loopback. Smoke требует положительный
process-local `keep-errors, sampled=true` counter напрямую и отдельно проверяет Prometheus query,
поэтому доказательство не зависит от WAL history. Повторный `make observability-smoke` с теми же
volumes является regression gate; volumes не очищаются.
