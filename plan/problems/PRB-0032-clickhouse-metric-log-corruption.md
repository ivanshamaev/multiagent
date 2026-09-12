# PRB-0032 — ClickHouse завершился из-за corrupted system.metric_log part

Status: resolved

Date: 2026-09-12

## Reproduction and cause

Fresh scenario reset получил Docker DNS error, потому что ClickHouse завершился с exit 139.
Server error log показал checksum mismatch в единственной части
`system.metric_log/202609_1465_1775_62`; `raw` и `analytics` не были затронуты.

## Fix and verification

После read-only проверки metadata удалена ровно повреждённая system telemetry part через
`ALTER TABLE system.metric_log DROP PART`. Volumes и business data не удалялись. ClickHouse снова
прошёл healthcheck, seed, 76/76 baseline dbt nodes и 13 SQL checks.
