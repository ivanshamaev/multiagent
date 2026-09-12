# PRB-0036 — DE repair overreached beyond accepted QA defect

- Status: resolved
- Detected: 2026-09-12
- Scope: live `QA FAIL → DE REWORK` proof

## Reproduction and cause

The refund-date mutation passed public validation and QA returned 62 semantic mismatches. The first
live Data Engineer repair corrected the date semantics but rewrote the whole mart around invented
`stg_marketing_attribution` and `stg_orders` refs. The mandatory second validator stopped at dbt
compilation; no second QA or publication occurred. The generic DE context did not contain the
current candidate file, so the model reconstructed it instead of applying a bounded repair.

## Fix and regression

The quality-loop runner now supplies a verified, bounded read of the exact current target and
requires the minimal `orders.order_date` replacement while preserving all other CTEs and refs.
The repair still receives one write call only. Success requires the full validator and a fresh QA
PASS; another overbroad rewrite remains fail-closed. Live workflow
`quality-net-revenue-20260912161215` then completed with one minimal write, two full validators and
final `QA_PASSED`.
