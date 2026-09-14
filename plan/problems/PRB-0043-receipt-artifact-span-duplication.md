# PRB-0043 — Receipt retry duplicated artifact telemetry

Status: resolved

Date: 2026-09-14

## Symptom and reproduction

Первичная реализация role telemetry вызывала общий `_complete_trace` и после нового handler result,
и после загрузки того же result из durable receipt. Повторный `AnalystExecutor.advance` с тем же
operation ID поэтому создавал второй `agentic.artifact`, хотя handler выполнялся один раз и новый
artifact не принимался.

## Cause

Receipt hit означает replay уже принятого role output для закрытия post-result/pre-checkpoint окна.
Код различал hit только attribute на role span, но не использовал этот признак при генерации
artifact spans.

## Fix

Role span сохраняется для каждого execution attempt и получает `agentic.receipt.hit=true`, но
artifact emission немедленно прекращается на cache hit. Artifact span создаётся только на первом
успешном role result для новых reducer events.

## Regression check

`test_receipt_retry_is_traced_without_reemitting_artifact` дважды запускает Analyst с одним typed
snapshot/carrier и durable receipt. Проверка требует один handler call, role spans `[false, true]`
с одинаковым operation ID и ровно один artifact span.
