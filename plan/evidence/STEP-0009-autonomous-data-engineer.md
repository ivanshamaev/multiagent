# STEP-0009 — Autonomous Data Engineer Evidence

Date: 2026-09-12

Status: PASS

## Verified result

The Data Engineer executes the frozen Net Revenue specification in an isolated workspace through
fresh investigation, SQL, test, and bounded repair conversations. Code owns identity, transitions,
budgets, atomic writes, evidence, and acceptance. The agent sees only role-scoped workspace/MCP
tools; it cannot access the grader, shell, protected paths, `.env`, or production. A four-gate
validator independently checks workspace integrity, full dbt build/tests, SQL correctness, and
repository policy before the unchanged hidden grader runs.

## Live model evidence

GateLLM exposes `CHAT`, `VISION`, and `IMAGE_GENERATION`, not a dedicated reasoning category.
GPT-5.4 Nano and GPT-5.6 Luna passed strict structured-output and forced-tool probes. Nano remained
less reliable on dbt semantics. The fixed Luna sample achieved 8/10 public validation and 7/10
end-to-end hidden success, with zero policy violations or protected-path changes. Successful public
runs had median 17,330.5 tokens, 34,843 ms model latency, and 1.940130 ₽ cost. The post-fix run
`3b0b2556cfdf` passed public and all five hidden checks after one repair: 27,768 tokens, 40,699 ms,
and 2.756280 ₽. Per-run records remain private mode 0600; aggregate outcomes are in
`STEP-0009-reliability-sample.md`.

## Commands and outcomes

- `make check` — exit `0`; Ruff/format PASS, 252 pytest checks PASS, Compose valid.
- `make mcp-smoke` — exit `0`; three allowed calls succeeded and DDL was denied before execution.
- `make scenario-repro-test` — exit `0`; baseline `88950d05…`, data `3823d7b5…`, source
  `a7efb5e5…` reproduced.
- `make platform-test` — exit `0`; Airflow/Cosmos 11/11, dbt 68/68, independent SQL checks PASS.
- Hidden grade for post-fix candidate — exit `0`; boundary, read-only, schema, invariants, and
  business-correctness checks PASS.
- `git diff --check` and tracked-diff secret scan — exit `0`; `.env` remained ignored.

## Residual risks

Measured end-to-end reliability is 70%, so Luna is a role-specific baseline rather than a general
guarantee. One public-valid candidate failed the hidden oracle, and model output remains
nondeterministic. The 42k ceiling makes two repair attempts executable but permits a worst-case
run near 4 ₽. These become QA/mutation and broader evaluation work; no validator or grader
assertion was weakened.
