# STEP-0015 — Controlled dev-DAG trigger

Status: complete

Date: 2026-09-13

Owner: repository maintainers

Updated: 2026-09-13

Current step: complete; proceed to Phase J planning.

## Goal

Complete the write slice of Phase I with one narrowly controlled trigger for the local manual
acceptance DAG. The capability must use a new Airflow identity and policy profile, require an
explicit short-lived human approval, derive an idempotent run ID in code, and retain typed evidence.

## Non-goals

- Production or scheduled-DAG write access; pause/unpause, clear, retry, backfill, task mutation,
  arbitrary run IDs/config, XCom, variables, connections, pools, config, or metadata DB access.
- Adding write operations to `airflow-observer-v1` or its six-tool MCP server.
- Letting an LLM create, broaden, renew, or self-approve an authorization.

## Affected layers and allowed paths

- Contracts/policy: `contracts/`, `policies/` and a new trigger-only profile.
- Runtime: a separate local Airflow trigger MCP/API adapter, approval store, facade, and live smoke.
- Platform: idempotent bootstrap of a dedicated least-privilege FAB identity.
- Tests/docs/evidence: `tests/`, `plan/`, root and Airflow documentation, Make/.env examples.

## Acceptance criteria

- Exactly one fixed `POST /api/v2/dags/{dag_id}/dagRuns` exists in the write server; only
  `ecommerce_acceptance` is eligible, while the observer remains byte-for-byte read-only in scope.
- The caller cannot choose method/path/origin/headers/JWT/run ID/`conf`; code derives a stable run ID
  from a bounded idempotency key and sends an empty configuration.
- A code-owned approval record binds approval ID, DAG, idempotency key, approver, creation/expiry,
  and one consumption. Missing, expired, mismatched, forged, or replayed approval fails before POST.
- MAF marks the trigger function `always_require`; direct gateway execution still cannot bypass the
  deterministic approval store.
- A new Airflow user has only the minimum live-verified FAB permissions needed for this endpoint;
  there is no admin fallback and no metadata-DB access.
- Same-key retry returns the original DAG run and never creates a second run, including after an
  ambiguous transport outcome. Successful and denied calls retain same-task typed evidence.
- Unit, policy, adversarial, live idempotency, observer regression, platform, scenario, and diff
  gates pass; services are stopped without deleting volumes.

## Implementation checklist

1. Record the separate identity/profile/approval/idempotency design in ADR-0025.
2. Inspect served OpenAPI and FAB permissions for create/read DAG-run operations.
3. Add closed approval and trigger contracts plus deny-by-default policy checks.
4. Implement secure atomic approval storage and a fixed-path trigger adapter with preflight lookup.
5. Add a separate MCP server/stdio client/MAF facade; keep observer registration unchanged.
6. Provision and verify the least-privilege Airflow identity idempotently.
7. Add unit/policy/adversarial tests and a live `approve → trigger → same-key retry → one run` gate.
8. Run full regressions, persist evidence, update roadmap/progress, and stop Compose.

## Risks and mitigations

- **Duplicate runs after timeout:** deterministic run ID plus GET-before-POST reconciliation.
- **Approval replay/race:** regular-file checks, mode 0600, atomic create/replace, file lock, expiry,
  exact field binding, and consumed terminal state.
- **Privilege creep:** separate user, profile, process, endpoint set, and live permission audit.
- **Secret leakage:** credentials stay in explicit subprocess env and errors never include request
  bodies, tokens, credentials, or approval contents.
- **Unsafe config injection:** request schema has no `conf`; adapter always sends `{}`.
- **Paused manual DAG:** the live fixture temporarily unpauses only `ecommerce_acceptance` and an
  `EXIT` trap restores it; the trigger identity has no pause/unpause operation.

## Planned verification

```bash
uv run pytest -q tests/unit/test_airflow_trigger.py tests/policy/test_airflow_trigger_profile.py
uv run pytest -q tests/adversarial/test_airflow_trigger_guards.py
make airflow-trigger-smoke
make airflow-mcp-smoke
make check
make mcp-smoke
make scenario-repro-test
make scenario-grade-baseline-test
make platform-test
git diff --check
make platform-down
```

## Actual result and work log

- Implemented the closed trigger contract, policy, approval store, fixed API adapter, standalone
  MCP/MAF facade, dedicated FAB identity, CLI and live gate.
- Live permissions were reduced to the exact custom-role set recorded in ADR-0025. PRB-0040 fixed
  Airflow CLI ordering and documented FAB's mandatory `can_read Website` permission.
- The first live run exposed the paused-DAG precondition. PRB-0041 added an admin-owned fixture
  unpause with an `EXIT` restore; the trigger identity gained no pause permission.
- `make airflow-trigger-smoke` proved `created → existing`, one run ID and 11/11 successful tasks.
  `make check` passed 371 tests; all planned MCP, scenario, grader and platform gates exited 0.
- Persistent evidence: `plan/evidence/STEP-0015-controlled-dev-dag-trigger.md`.
