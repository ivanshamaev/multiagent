# STEP-0020 evidence — branching, rework and role idempotency

Date: 2026-09-14

## Proven behavior

- `agentic-data-role-pipeline-v2` routes only decoded reducer stages through named MAF switch/case
  predicates. `BLOCKED`, `FAILED` and `DONE` converge on one validating terminal executor.
- Validator, QA and Reviewer failures enter the shared bounded `REWORK → DE → Validator → QA →
  Reviewer` route. Prior accepted implementation/gate artifacts move into immutable `gate_history`.
- A zero rework budget converts requested rework into terminal `FAILED`; downstream roles do not run.
- Every role operation has a deterministic input-bound receipt. Existing identical receipt is a
  cache hit; mode, symlink, path escape, malformed content, hash mismatch and collision fail closed.
- Process recovery killed DE after its receipt was durable but before its MAF output/checkpoint.
  Resume from the PM checkpoint reached `DONE` with every persisted role call count equal to 1.

## Commands

```text
make role-pipeline-test
# exit 0 — 13 passed

make check
# exit 0 — Ruff PASS; format PASS; 395 passed; plan governance PASS; Compose config PASS

docker compose ps --format json
# exit 0 — no running services
```

No GateLLM call or Data Platform mutation was required. Existing role/provider/platform suites remain
green; this step validates control-plane routing and crash semantics deterministically.

## Residual risk

A crash after an external system commits but before the handler returns cannot be solved by a local
post-result receipt. Such tools need the supplied deterministic operation identity or explicit
reconciliation. Receipt/checkpoint retention and distributed storage remain future work.
