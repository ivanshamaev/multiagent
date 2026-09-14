# PRB-0048 — Internal-only Docker network suppressed loopback publications

Status: resolved

Date: 2026-09-14

## Symptom and reproduction

После исправления Tempo все четыре контейнера работали, `HostConfig.PortBindings` содержал
loopback mappings, но `NetworkSettings.Ports` оставался пустым, `docker compose ps` не показывал
порты и host smoke получал connection refused.

## Cause

В используемом Docker Engine 28.1 контейнеры только на `internal: true` bridge не получили gateway
для публикации host ports. Одна общая non-internal сеть нарушила бы изоляцию backend traffic.

## Fix and regression

Каждый сервис подключён к общей internal backend network и к собственной одно-сервисной host bridge.
Поэтому межсервисные имена разделяют только internal network, а loopback publication получает
gateway без общей egress-сети. Live smoke проверяет все четыре host endpoints; policy test проверяет
internal backend и четыре отдельные host bridges.
