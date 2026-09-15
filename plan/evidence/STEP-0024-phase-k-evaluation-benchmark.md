# STEP-0024 — Phase K evaluation benchmark evidence

Date: 2026-09-15

Status: PASS

## Delivered boundary

- Versioned 17-case suite covers five reliability, five quality-gate and seven safety cases.
  Each runs three times in a fresh sanitized pytest subprocess with fixed hash seed, 30s timeout
  and bounded output; timeout/overflow kills the subprocess group.
- Fingerprint covers canonical suite/strict baseline and content hashes of prompts, Python runtime,
  contracts, policies, scenarios, tests, lock/config and Makefile. Missing/symlink/escaping inputs
  and mid-run configuration changes fail closed.
- Reports contain outcome/duration/output digest only, never raw pytest/model/tool output.
  Reports are atomically stored under ignored `.scenario-state/evaluations/` (0700/0600).
- Baseline requires 100% overall/reliability/quality/safety and zero policy violations/tokens/cost.
  Incomplete samples, shell manifests, extra command fields and unsafe report filenames are rejected.
- Dated historical live provenance indexes 24 existing attempts separately; no current model-quality
  rerun is claimed and no paid API calls were made.

## Verification

`make evaluation-test`: exit 0, 13 tests. Final two benchmark samples and `make check` are recorded
below. `flock -n .scenario-state/offline-validation.lock true` returned 1 while
benchmark held the lock (expected contention), confirming no second owner was admitted.

Superseded pre-PRB-0052 configuration fingerprint (not the final baseline):
`59e6e6f22cace949960aa4647eccb4575251f79e5da1290a1bc1008ca349bfc1`.

| Command | Result |
| --- | --- |
| `make evaluation-test` | exit 0; 13 passed |
| exploratory pre-PRB-0052 run A | exit 0; 51/51 PASS; p50 2033ms, p95 6149ms |
| exploratory pre-PRB-0052 run B | exit 0; 51/51 PASS; p50 2037ms, p95 6104ms |

Run A has overall/reliability/quality/safety pass rates 1.0; zero assertion failures, timeouts,
harness errors, policy violations, offline tokens and offline cost.

## Final post-fix sample

Configuration fingerprint:
`ecaf7e7fa8acb2c30874226506c6d3cbcd509e4fceb1e71c6710476d548d71a3`.

| Command | Result |
| --- | --- |
| checkpoint unit + process recovery tests | exit 0; 7 passed |
| `make evaluation-benchmark EVALUATION_REPORT_NAME=phase-k-run-a.json` | exit 0; 51/51 PASS; p50 2026ms, p95 6231ms |
| `make evaluation-benchmark EVALUATION_REPORT_NAME=phase-k-run-b.json` | exit 0; 51/51 PASS; p50 2033ms, p95 6193ms |
| `make check` | exit 0; 451 tests PASS; Ruff/format (155 files), governance, Compose PASS |
| report/current fingerprint comparison | exit 0; both match unchanged repository configuration |
| report modes | directory 0700; both reports 0600 |
| `git diff --check` | exit 0 |
| `docker compose --profile observability ps --format json` | exit 0; empty |

Final sample totals 102/102 PASS, all three category rates 1.0, zero assertion failures/timeouts/
harness errors/policy violations/offline tokens/cost. Report SHA-256:

- `.scenario-state/evaluations/phase-k-run-a.json`:
  `de73ae22b6f95f8120269877e0fca82ea3bbfe55b1145e8ef941996119cbec88`.
- `.scenario-state/evaluations/phase-k-run-b.json`:
  `55ec35bec12b83d2b4ab84d499aa05bf2536f22c3575b0522560e4eaa25f3fe0`.

## Problems and remaining risks

ADR-0033 defines the two-layer evaluation boundary; EXP-0005 records repeatability. PRB-0050 fixed
pytest module naming; PRB-0051 fixed concurrent Make test/benchmark shared-fixture mutation. The
exploratory full check failed with 449 PASS/one fixture-race failure before this fix. Exploratory
benchmark invocations invalidated by configuration changes are excluded from final evidence.
The next full check reproduced PRB-0052: checkpoint reader observed publication before chmod
(449 PASS/one FAIL). The scoped fix stages MAF encoding privately and publishes a fully written
0600 file using create-only atomic hard-link. A deterministic reader regression is added;
final samples below must use the post-fix fingerprint. A killed writer can leave an owner-only
staging directory; readers ignore it and automated garbage collection remains deferred.

This is a trusted repository-owned regression harness, not an arbitrary-code/network sandbox.
Direct pytest and other scenario-mutating commands must not overlap the benchmark. Timing is
reported, not an SLO threshold. Historical DE success remains 70%; null historical fingerprints
remain unknown. Future model/prompt/tool changes need a fresh explicitly budgeted live evaluation.
Data Platform and observability services remain stopped; no Docker volume was removed.
