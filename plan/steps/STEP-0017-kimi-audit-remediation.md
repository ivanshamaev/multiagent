# STEP-0017 — Kimi audit remediation

Status: complete

Date: 2026-09-13

Owner: repository maintainers

Updated: 2026-09-13

Current step: complete; carry explicit isolation/hardening backlog into Phase J.

## Goal

Turn `plan/kimi_k3_review.md` into a repository-grounded disposition and fix confirmed,
bounded findings before Phase J. Preserve the audit unchanged as external evidence.

## Non-goals

- Replacing Phase J reliability/observability/isolation or Phase K benchmark work.
- Large runtime refactors, changing the OpenAI/MAF stack, or claiming repository-local grader code
  is confidential.
- Rewriting historical records merely to normalize style.

## Scope and acceptance criteria

1. Classify every F-01…F-22 as fixed, accepted, deferred with owner/target, or not reproduced.
2. Close immediate governance drift: STEP-0015 trail, PRB statuses/naming/indexes, ADR index,
   missing STEP-0001 evidence, current contributor commands and factual observability wording.
3. Make `.env` owner-only now and enforce safe mode during bootstrap without reading its content.
4. Record an ADR for the verified `httpx2` provenance and residual supply-chain controls.
5. Digest-pin the exact ClickHouse image already used by the validated platform.
6. Add a deterministic plan linter to `make check` for names, statuses, indexes and required
   sections; include regression tests.
7. Record larger hermetic-test, identity, duplication and runtime-hardening items as explicit
   Phase J backlog rather than mixing them into an unauditable mega-refactor.
8. Run focused tests, `make check`, scenario/platform regressions, secret/diff audit, then stop
   Compose without deleting volumes.

## Risks

- Historical normalization can destroy useful evidence: preserve content and use explicit
  disposition instead of bulk rewriting old files.
- A digest copied from the wrong architecture can break pulls: derive it from the locally validated
  tagged image and validate Compose.
- Governance lint can produce false positives: constrain it to stable, documented invariants and
  test both pass and failure cases.
- `.env` handling must never print or parse secrets; inspect and change only filesystem mode.

## Verification

```bash
uv run pytest -q tests/policy/test_plan_governance.py
make check
make scenario-repro-test
make scenario-grade-baseline-test
make platform-test
git diff --check
make platform-down
```

## Actual result and work log

- F-01 was stale against the post-audit repository: STEP-0015 already has work log, progress and
  passing evidence. All other findings were reproduced or rejected against code rather than copied.
- Closed immediate governance/security/platform items: `.env` 0600 enforcement, full indexes,
  unique PRB-0042, stale statuses, STEP-0001 evidence, ADR back-links, current runbooks, factual
  observability wording and a digest-pinned ClickHouse image.
- Added `make plan-check` with pass/fail policy tests. It enforces names, unique IDs, allowed
  statuses, indexes, completed-step evidence and at most one active step.
- ADR-0026 records verified Pydantic/OpenAI HTTPX2 provenance and residual controls. Removed the QA
  optimization-sensitive assert and corrected the live Reviewer profile tuple.
- Deferred only cohesive Phase J/K work: hermetic test workspaces/import cleanup; common runtime
  security helpers and validated updates; grader/Airflow identities and JWT refresh; coverage/live
  markers; heuristic cleanup and supported-surface deprecation.
- `make check` passed 374 tests. Scenario reproducibility, baseline grader and digest-pinned
  platform/Cosmos/dbt 68/68 gates passed. Full disposition and evidence are in
  `plan/evidence/STEP-0017-kimi-audit-remediation.md`.
