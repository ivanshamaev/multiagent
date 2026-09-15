# EXP-0005 — Repeated offline Phase K benchmark

Date: 2026-09-15

## Hypothesis and protocol

The built workflow/rework/recovery, quality-gate and authorization boundaries pass a strict
repeated offline regression baseline with stable configuration identity. This does not test current
LLM reasoning. Suite `phase-k-regression-v1`, protocol `offline-pytest-v1`: 17 distinct cases,
three repetitions, fresh pytest process per case, 30s timeout and 262144-byte output bound.

## Configuration and provenance

Scenario: `net-revenue-v1` plus policy/recovery boundary cases. Baseline: 100% overall/reliability/
quality/safety, zero policy violations, zero offline tokens/cost. Provider/model: none (offline).
Prompt/tool/policy versions: content hashes of repository inputs; no instructions were changed.
Code revision: `14756cdac09d1a64eb1a79ae1d63af1c72e8f4cf` plus STEP-0024 working changes;
the final configuration fingerprint and report metrics are retained in STEP-0024 evidence.

## Failures and controls

PRB-0050 fixed duplicate pytest module names. PRB-0051 reproduced concurrent scenario-fixture
mutation, then serialized Make test/benchmark targets with one lock. An exploratory run was
invalidated by the configuration-change guard while implementation continued; it is excluded
from the final sample. No failed baseline was weakened or promoted.
PRB-0052 subsequently exposed checkpoint publication-before-chmod during the full gate. The two
passing pre-fix samples are superseded; final samples are repeated after atomic owner-only
checkpoint publication and deterministic regression coverage.

## Results and conclusion

Final sample: two complete benchmark invocations, 51 subprocess attempts each (102 total).
Result: 102/102 PASS, category rates 1.0, zero violations/tokens/cost. Fingerprint:
`ecaf7e7fa8acb2c30874226506c6d3cbcd509e4fceb1e71c6710476d548d71a3`.
Run A p50/p95: 2026/6231ms; run B: 2033/6193ms. Full gate: 451 tests PASS (exit 0).
Exact commands and report digests: `plan/evidence/STEP-0024-phase-k-evaluation-benchmark.md`.
Historical 24 live attempts are separately indexed, explicitly not a current rerun. DE historical
success is 70%, not 100%; offline PASS must never overwrite that model-quality result. Missing
historical fingerprints remain null rather than invented.

## Follow-up

Use the offline suite for boundary regressions. Model/prompt/tool changes require a fresh budgeted
live sample with catalog/pricing snapshot and matched scenario provenance. Next roadmap phase is
Phase L: build practical course modules from verified decisions, problems and evidence.
