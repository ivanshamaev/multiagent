# PRB-0041 — Controlled trigger smoke stalled on a paused DAG

Status: resolved

Date: 2026-09-13

## Symptom and reproduction

`make airflow-trigger-smoke` created exactly one deterministic `ecommerce_acceptance` run, then
timed out while polling it. The metadata record and all 11 task instances remained `queued`/unset.
The defect reproduced whenever the manual DAG retained its repository-default paused state.

## Root cause

Airflow accepts a DAG-run POST for a paused DAG but the scheduler does not start that run. The new
write adapter intentionally cannot pause or unpause DAGs, while the initial live harness omitted
the operational readiness precondition used by the existing Airflow API acceptance test.

## Accepted fix

The Make live gate uses the existing admin-only test fixture to unpause the single manual DAG before
the trigger smoke and a shell `EXIT` trap to restore paused state on success, failure, or interrupt.
The trigger MCP identity and adapter remain unable to PATCH a DAG, and the production-like hourly
DAG is never unpaused.

## Regression check

`make airflow-trigger-smoke` must complete the 11-task run, prove `created_then_existing`, and leave
`ecommerce_acceptance` paused. Policy/adversarial tests continue to reject pause or arbitrary HTTP
operations from the trigger boundary.
