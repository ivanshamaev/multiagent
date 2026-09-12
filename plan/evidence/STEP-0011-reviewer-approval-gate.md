# STEP-0011 evidence — Independent Reviewer approval gate

Completed: 2026-09-13

## Delivered boundary

`reviewer_v1` exposes only two bounded candidate reads and denies write, SQL/dbt/shell, grader,
secrets, protected paths, wrong role, and production. Two fresh MAF phases retain positive model
observations and inspect the contract test. Code owns IDs, evidence links, exact criterion coverage,
budgets, authorship, and `QA_PASSED → REVIEW → DONE|REWORK|BLOCKED` transitions. An accepted change
request can return only through DE, all four validator gates, fresh QA, and fresh Reviewer; an
integration test proves that complete sequence.

## Verification

- `make check` — exit 0; Ruff/format/Compose green; 305 pytest tests passed.
- Reviewer targeted policy/unit/integration/workflow suite — exit 0; 38 tests passed.
- `make mcp-smoke` — exit 0; three allowed calls and expected ClickHouse DDL denial.
- `make scenario-repro-test` — exit 0; stable baseline/data/source fingerprints.
- `make scenario-grade-baseline-test` — exit 0; intentionally `INCOMPLETE` baseline with only
  submission-boundary/read-only checks.
- `make platform-test` — exit 0; Airflow/Cosmos 11/11, dbt 68/68, independent SQL green.
- Canonical `scenario-run`, `scenario-contract-test`, `scenario-grade` — exit 0; dbt 78/78, public
  SQL PASS, hidden grader all five checks PASS.
- `git diff --check` and token-pattern scan — exit 0; no retained API key.

## Live evaluation

GPT-5.6 Luna: canonical `APPROVE`, 4/4 mutations `REQUEST_CHANGES`, false approval 0/4. Each run
made two Reviewer file reads and cost 1.227000–1.592700 ₽. Safe private records are under
`.scenario-state/runs/qa-reviewer-review-net-revenue-*.json` and remain ignored/mode 0600.
GPT-5.4 Nano repeatedly false-rejected canonical; Poolside Laguna XS failed closed. Details are in
`EXP-0004` and `PRB-0037`.

Residual risk: the live sample is one run per accepted Luna configuration, mutation findings can
reference a semantically adjacent criterion, and role reliability still needs the repeated-run
benchmark planned in Phase K.
