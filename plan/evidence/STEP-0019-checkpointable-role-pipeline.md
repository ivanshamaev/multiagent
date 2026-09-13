# STEP-0019 evidence — checkpointable six-role pipeline

Date: 2026-09-13

## Proven behavior

- MAF graph: `role_analyst → role_pm → role_data_engineer → role_validator → role_qa →
  role_reviewer`.
- Successful deterministic run: final stage `DONE`, revision 12, checkpoint iterations 0…6.
- Every edge carries canonical JSON and reconstructs a strict `RolePipelineSnapshot`; checkpoint
  payloads contain no `runtime.role_pipeline` Python type marker.
- Boundaries reject oversized/unknown fields, wrong stage, tampered event chain, changed identity,
  rewritten history/artifacts and out-of-order artifacts.
- Recovery: worker was killed at Validator entry after iteration 3 (Data Engineer committed). A new
  process restored that exact checkpoint and reached `DONE`; each role's persisted call count was 1.

## Commands

```text
make role-pipeline-test
# exit 0 — 4 passed

make check
# exit 0 — Ruff PASS; format PASS; 386 passed; plan governance PASS; Compose config PASS

docker compose ps --format json
# exit 0 — no running services
```

No GateLLM request or Data Platform mutation was needed. This is a control-plane recovery proof;
provider, tool and platform behavior remains covered by their existing integration/live gates.

## Residual risk

MAF persists only after an executor returns. If a process dies after an external write but before
that checkpoint, the current role may be invoked again; its effects therefore require idempotency.
Failure/rework routing, OTel spans and separate runner identities are intentionally deferred.
