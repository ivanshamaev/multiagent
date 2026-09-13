# STEP-0018 — Checkpoint, resume, and crash recovery

Status: complete

Date: 2026-09-13

Owner: repository maintainers

Updated: 2026-09-13

Current step: complete; next Phase J slice is production role-graph decomposition/checkpointing.

## Goal

Begin Phase J with a durable local checkpoint/resume slice. A process killed after one committed
MAF superstep must restart from that checkpoint, execute the pending next stage exactly once, and
never rerun the completed stage.

## Non-goals

- Claiming all role workflows are resumable; current single-executor role internals need a later
  graph decomposition before checkpoints can exist between every business stage.
- OTel Collector/Jaeger, dashboards, production storage, distributed locking, Kubernetes, or
  production credentials. These remain later Phase J work.
- Deserializing checkpoints supplied by an untrusted principal.

## Design and affected paths

- ADR-0027 defines MAF-native checkpoints, a repository-owned hardened storage wrapper and the
  trusted-local boundary.
- `runtime/checkpoints.py` owns repository containment, names, mode 0700/0600, symlink rejection,
  fail-closed load/list and the MAF storage adapter.
- `runtime/checkpoint_smoke.py` builds a stable two-stage graph and orchestrates a real child-process
  kill/restart. Only JSON-safe primitive messages are checkpointed.
- `tests/unit/` and `tests/integration/` cover storage tampering, incompatible graphs, exact-once
  completed-stage behavior and recovery. Make exposes a non-LLM `checkpoint-smoke` gate.

## Acceptance criteria

1. Checkpoints stay under `.scenario-state/checkpoints`, directory is 0700 and files are 0600.
2. Unsafe IDs, roots/files outside the repository, symlinks, loose modes, malformed payloads and
   incompatible workflow graphs fail closed before resume.
3. The crash gate waits for a durable checkpoint, terminates the first process, reconstructs the
   graph, resumes by checkpoint ID and produces the expected output.
4. A durable counter proves the already committed first stage ran once, not from task zero; the
   resumed second stage also completes once.
5. No prompt, model call, secret, arbitrary pickle type or Data Platform container is involved.
6. Focused tests, `make check`, scenario/platform regressions and `git diff --check` pass; Compose
   is stopped without deleting volumes.

## Risks and mitigations

- MAF file checkpoints use restricted pickle markers for framework objects: accept only local
  mode-protected files, register no application types and never treat this as an untrusted format.
- Killing before the committed boundary makes resume impossible: the harness waits for the second
  checkpoint (entry plus first superstep) and fails with a bounded timeout.
- Resume against changed topology: stable workflow name plus MAF graph-signature validation.
- Duplicate side effects inside a superstep remain possible: only committed-stage non-reexecution
  is claimed; external writes still require their existing idempotency controls.

## Planned verification

```bash
uv run pytest -q tests/unit/test_checkpoints.py tests/integration/test_checkpoint_recovery.py
make checkpoint-smoke
make check
make scenario-repro-test
make scenario-grade-baseline-test
make platform-test
git diff --check
make platform-down
```

## Actual result and work log

- Inspected pinned MAF 1.17 checkpoint contracts and verified checkpoints occur at entry and after
  each superstep. ADR-0027 selected the framework state/messages/signature model behind a hardened
  adapter; no second orchestration runtime was introduced.
- Implemented UUID-only, repository-contained, create-only storage with 0700/0600 modes, size
  bounds, symlink/escape/loose-mode rejection and fail-closed restricted decoding.
- Added a stable two-executor graph and child-process harness. The parent waits for iteration 1 and
  pending finish-stage execution, sends `SIGKILL`, reconstructs the graph and resumes by ID.
- Two live smoke runs returned `start_stage_calls=1`, `finish_stage_calls=1`, `resumed=true`.
  Checkpoint/sentinel/counter files had only 0700/0600 modes and no inherited GateLLM environment.
- Focused tests passed 14 checks; `make check` passed 381. Scenario reproducibility, isolated
  grader, Airflow/Cosmos, dbt 68/68 and independent SQL gates all exited 0.
- Evidence: `plan/evidence/STEP-0018-checkpoint-resume-crash-recovery.md`.

## Remaining risks

- Existing role pipelines still perform multiple business phases inside one executor, so their only
  checkpoints are entry/completion. The next slice must split a real pipeline at typed handoffs.
- Checkpoints are integrity-protected by access controls and MAF topology/type validation, not a
  signature; same-user tampering is outside this trusted-local boundary.
- An interrupted external side effect inside an uncommitted superstep can repeat. Tool-specific
  idempotency remains mandatory, as demonstrated by the Airflow trigger.
