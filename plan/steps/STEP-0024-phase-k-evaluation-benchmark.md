# STEP-0024 — Phase K: evaluation and regression benchmark

Status: completed

Owner: Codex

Updated: 2026-09-15

## Goal

Создать воспроизводимый evaluation benchmark поверх реально построенных boundaries: не менее десяти
versioned cases, repeated-run protocol, immutable configuration fingerprint, typed metrics/failure
taxonomy и baseline comparison. CI benchmark должен проверять quality, reliability и safety без
GateLLM/Data Platform; прошлые live samples остаются отдельным model-quality evidence layer.

## Non-goals

- обучение/дообучение модели, изменение prompts, tools, grader или acceptance criteria;
- новый платный 10-run GateLLM sample при неизменной model configuration;
- production load/SLO test, distributed benchmark service или внешняя SaaS eval platform;
- включение prompts, raw model/tool outputs, API credentials или hidden grader internals в report;
- Phase L course authoring.

## Affected layers and allowed paths

- `evals/phase_k/**`: versioned suite, thresholds и historical-live provenance;
- `runtime/evaluation_benchmark.py`: fail-closed runner, fingerprint, metrics/report;
- `tests/{unit,policy,adversarial}/`, `Makefile`;
- `plan/`, `README.md`, `AGENTS.md`, `Claude.md`.

Agent prompts, role/runtime behavior, policy profiles, scenarios and grader remain unchanged; they
are hashed inputs and test subjects only.

2026-09-15 scope amendment: `runtime/checkpoints.py` and `tests/unit/test_checkpoints.py` are allowed
for the reproduced PRB-0052 publication-mode race. Publish only fully written mode-0600 checkpoints
with atomic create-only semantics; retain the MAF encoding and existing reader permission checks.
Repeat final benchmark evidence after this fix; no role transitions or policy changes are authorized.

## Acceptance criteria

1. Manifest содержит ≥10 unique cases across reliability, quality and safety, включая
   prompt/tool-output poisoning, permission escalation, rework, crash recovery and quality gates.
2. Default protocol выполняет каждый case минимум трижды in fresh pytest processes, с fixed
   `PYTHONHASHSEED`, bounded timeout/output и environment без `API_TOKEN`/provider secrets.
3. Configuration fingerprint включает canonical suite/baseline и content hashes prompts,
   contracts, policies, runtime, scenarios and selected tests; symlink/escape/missing inputs fail.
4. Typed mode-0600 report содержит per-run outcome/duration, aggregate pass rates, p50/p95,
   zero offline tokens/cost, policy violations, failure taxonomy и baseline regression verdict.
5. Baseline требует 100% offline overall/safety/quality/reliability, zero violations/tokens/cost;
   снижение threshold запрещено policy test. Failed/timeout/harness cases дают non-zero exit.
6. Historical live baseline агрегирует только уже зафиксированные EXP/evidence metrics с source
   links/fingerprint и явно не выдаётся за current rerun.
7. `make evaluation-test`, два `make evaluation-benchmark`, `make check` проходят; reports имеют
   одинаковый configuration fingerprint/verdict, runtime containers остаются stopped.

## Risks, permissions and approvals

- Suite executes only repository-owned allowlisted pytest node IDs; arbitrary command/shell fields
  in manifest are forbidden. Subprocess timeout kills the process group.
- Benchmark writes only ignored `.scenario-state/evaluations/**`; directory 0700, report 0600,
  atomic replacement. No Docker, MCP, network or GateLLM calls are needed.
- Historic live numbers may not represent current code. They are provenance, not a green current
  model regression. A future prompt/model/tool change requires an explicitly paid fresh sample.
- Existing uncommitted STEP-0023 work is preserved and not rewritten outside documented updates.

## Implementation checklist

- [x] Accept ADR-0033 for two-layer offline/live evaluation and threshold baseline.
- [x] Add closed suite/baseline/live-provenance manifests with at least ten cases.
- [x] Implement safe repeated runner, fingerprint, typed report and regression comparator.
- [x] Add Make targets and unit/policy/adversarial coverage.
- [x] Run repeated benchmark twice, document metrics/failures and persistent evidence.
- [x] Run full gates, update roadmap/runbooks, and leave services stopped.

## Verification

Expected: `make evaluation-test`, `make evaluation-benchmark` twice, `make check`,
`git diff --check`, empty `docker compose ps`. Actual results are recorded after execution.

Final: targeted 13 tests PASS; checkpoint/recovery 7 tests PASS; two unchanged post-fix samples
51/51 PASS each with fingerprint `ecaf7e7fa8acb2c30874226506c6d3cbcd509e4fceb1e71c6710476d548d71a3`;
`make check` exit 0 (451 tests, Ruff, governance, Compose). Reports 0600, directory 0700;
services stopped. Persistent summary: `plan/evidence/STEP-0024-phase-k-evaluation-benchmark.md`.

## Decisions and problems

- ADR-0033 is created before implementation.
- Systematic defects require reproduction, cause, fix and regression record.

## Work log

- 2026-09-14: Phase K opened; existing DE 10-run, QA/Reviewer mutations, Analyst cases and
  adversarial/recovery tests inventoried before defining the benchmark.
- 2026-09-14: PRB-0050 fixed a pytest basename collision before any benchmark case executed;
  combined targeted selection is the regression gate.
- 2026-09-15: Added real timeout/output-limit, incomplete-sample and symlink regressions. PRB-0051
  reproduced a shared scenario-fixture race between check and benchmark; Make targets now hold a
  common lock. Exploratory reports are superseded by two final unchanged-configuration samples.
- 2026-09-15: PRB-0052 reproduced MAF publication-before-chmod in the full recovery gate. Scope
  amended before implementing staged owner-only create-only publication; final samples repeated.
