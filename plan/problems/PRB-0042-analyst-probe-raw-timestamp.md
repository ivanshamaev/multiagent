# PRB-0042 — Analyst probe used a mart timestamp name

Status: resolved

Date: 2026-09-13

## Reproduction

`make analyst-live ANALYST_MODEL=openai/gpt-5.6-luna SCENARIO=net-revenue` reached the immutable
ClickHouse profile and failed with `UNKNOWN_IDENTIFIER`: `raw.orders` has `ordered_at`, not the
derived mart field `order_date`.

## Cause and fix

The code-owned pre-PM probe incorrectly reused downstream mart vocabulary at the raw-source
boundary. The aggregate now profiles `min(ordered_at)` and `max(ordered_at)`. The failure was safely
retained by the MCP gateway and no `RequirementsAnalysisReport` crossed the reducer gate.

## Regression check

The Analyst policy test asserts that the immutable query contains `ordered_at` and not `order_date`.
The live command passed after unit and policy checks. This record replaces the colliding historical
name `PROBLEM-0011-analyst-probe-raw-timestamp.md` without changing the finding.
