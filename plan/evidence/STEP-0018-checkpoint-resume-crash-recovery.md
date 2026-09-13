# STEP-0018 evidence — checkpoint, resume, and crash recovery

Date: 2026-09-13

Status: PASS

## Implemented boundary

- `SecureCheckpointStorage` adapts MAF `FileCheckpointStorage` without replacing framework
  checkpoint semantics. Storage is repository-contained, 0700/0600, UUID-only, create-only,
  size-bounded and rejects symlinks, escapes, loose modes, malformed files and unexpected entries.
- No application type is registered with the restricted checkpoint decoder. Files are trusted local
  control-plane state and never model/tool input.
- A stable two-stage MAF graph commits stage one and its pending message at iteration 1. The live
  harness waits for that durable boundary, kills the process with `SIGKILL`, constructs a fresh
  workflow and resumes stage two from the checkpoint.

## Verification

| Command | Exit | Result |
| --- | ---: | --- |
| focused checkpoint/policy tests | 0 | 14 passed |
| `make checkpoint-smoke` (twice) | 0 | start=1, finish=1, resumed=true, iteration=1 |
| `make check` | 0 | Ruff, format, 381 tests, plan lint and Compose PASS |
| `make scenario-repro-test` | 0 | source/data/baseline fingerprints matched across resets |
| `make scenario-grade-baseline-test` | 0 | expected isolated `INCOMPLETE` boundary result |
| `make platform-test` | 0 | Airflow/Cosmos, dbt 68/68 and independent SQL PASS |
| `git diff --check` | 0 | no whitespace errors |

The durable smoke artifacts use 0700 directories and 0600 checkpoint/counter files. The child
environment contains only `PATH` and `PYTHONHASHSEED`; no LLM call, API token or Data Platform
container participates in recovery.

## Residual scope

This proves the recovery primitive, not end-to-end role recovery. Existing role workflows must be
decomposed into typed multi-executor graphs before they can resume between Analyst/PM/DE/QA/Review
business stages. OTel export and runner isolation remain later Phase J steps.
