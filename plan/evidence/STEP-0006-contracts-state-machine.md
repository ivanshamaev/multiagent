# STEP-0006 — Contracts and State Machine Evidence

Date: 2026-09-06

Status: PASS

## Verified result

Version-one Pydantic contracts reject unknown fields, invalid IDs, non-UTC timestamps, invalid
statuses and incomplete evidence. The workflow is an immutable pure reducer with an explicit
transition table. It verifies artifact type, decision, task, producer, implementation authorship
and deterministic resource charges before changing state. A bounded rework request becomes
`FAILED` when its budget is exhausted without recording usage above the configured limit.

Accepted transitions produce canonical SHA-256 chained events. Verification detects mutation,
reordering, replay and truncation when compared with expected state. This is an integrity chain,
not an authenticated durable log; persistence remains future work.

## Commands and outcomes

- Targeted Ruff/format and contract/workflow/policy/adversarial pytest — exit `0`; 41 passed.
- `make check` — exit `0`; Ruff PASS, 36 files formatted, 101 pytest checks PASS, Compose valid.
- `make scenario-repro-test SCENARIO=net-revenue` — exit `0`; both resets reproduced
  `baseline=53bf4b7d…`, `source=798def11…`, `data=3823d7b5…`.
- `make scenario-grade-baseline-test SCENARIO=net-revenue` — exit `0`; isolated grader returned
  expected baseline `INCOMPLETE` (contained exit `10`).
- `make platform-test` — exit `0`; Airflow run
  `api_smoke_20260906T063446010862Z_a587e8dd` completed 11/11 tasks; dbt 68/68 and independent
  ClickHouse assertions passed.
- `git diff --check` — exit `0` before final documentation update.

No GateLLM completion was called and no Docker volume was deleted. Remaining risks: event storage
is in-memory, SHA-256 does not prove authorship, and no MAF/provider adapter consumes these
contracts yet. Those boundaries are the scope of STEP-0007.
