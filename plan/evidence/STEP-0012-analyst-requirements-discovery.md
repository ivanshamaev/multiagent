# STEP-0012 evidence — Analyst requirements discovery

Date: 2026-09-13

Status: PASS

## Delivered boundary

- ADR-0022 changes the reducer order to `CREATED → ANALYZING → ANALYSIS_READY → SPECIFYING →
  SPEC_READY → IMPLEMENTING`; direct PM and DE bypasses are rejected.
- `RequirementsAnalysisReport` separates pre-PM discovery from legacy technical `AnalysisReport`.
  Facts carry code-owned IDs and successful same-task evidence references.
- `analyst_v1` has no writes/build/tests/shell. It permits only bounded workspace metadata, dbt
  list/lineage/details, and ClickHouse `SELECT` over `raw`/`analytics`.
- Three fresh tool phases use exact zero-argument facades for dbt inventory, `fct_orders` lineage,
  and a code-owned aggregate profile. Synthesis is tool-free. Fact text must be an exact excerpt of
  its retained tool result.
- Typed PM handoff binds request, reducer-accepted report, unresolved questions, workflow, task, and
  configuration fingerprint. PM reasoning remains STEP-0013.

## Verification

- `make check` — exit 0: Ruff, format, Compose and 322 tests passed (final equivalent rerun after
  the tool-free failure regression).
- `make mcp-smoke SCENARIO=net-revenue` — exit 0: three successful calls and expected DDL denial.
- `make scenario-repro-test SCENARIO=net-revenue` — exit 0; all fingerprints reproduced.
- `make scenario-grade-baseline-test SCENARIO=net-revenue` — exit 0; isolated grader returned the
  expected baseline `INCOMPLETE` and proved its submission/read-only boundary.
- `make platform-test` — exit 0; Airflow/Cosmos 11/11 tasks, ClickHouse checks, dbt 68/68 passed.
- Strict live canonical `analyst-net-revenue-canonical-e9bc5e5fea51` — PASS, `ANALYSIS_READY`, 25
  facts, 3 tools, 4 model calls, 14,120 tokens, estimated 1.362000 ₽.
- Strict live ambiguity `analyst-net-revenue-ambiguous-metric-69e73c121290` — PASS,
  `matched_expectation=true`, 9 questions, 3 tools, 4 calls, 14,109 tokens, estimated 1.324440 ₽.
- Private mode-0600 live records are under `.scenario-state/runs/`; prompts, responses and
  `API_TOKEN` are absent from persistent summaries.

## Problems and residual risk

PROBLEM-0011 records the initial raw timestamp mismatch and regression. Two live cases do not
establish statistical reliability. The profile currently covers orders only; the report correctly
keeps payment/refund/attribution schema questions unresolved. The legacy standalone PM adapter
temporarily creates labelled compatibility discovery from verified context; STEP-0013 must remove
it and consume the real typed handoff.
