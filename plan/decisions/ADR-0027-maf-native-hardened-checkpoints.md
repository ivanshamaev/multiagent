# ADR-0027 — MAF-native checkpoints behind a hardened local store

Status: accepted

Date: 2026-09-13

## Context

Phase J requires restart from a committed workflow boundary rather than rerunning from task zero.
Microsoft Agent Framework already captures messages, executor/shared state, pending requests,
iteration count and graph signature. Reimplementing those semantics would create a second workflow
runtime. Its file backend, however, does not enforce repository containment or owner-only modes and
uses restricted pickle markers for non-JSON framework values.

## Decision

Use MAF `WorkflowCheckpoint` and `FileCheckpointStorage` through a repository-owned adapter. The
adapter permits a fixed contained root, UUID checkpoint IDs, regular non-symlink files, 0700/0600
modes and fail-closed load/list. No application checkpoint types are registered. Checkpoints are
trusted local control-plane state, never agent/model/tool input.

The first proof uses two real executors and stable graph identity. A separate process is killed only
after the first superstep checkpoint is durable; a fresh graph resumes the pending message. This
proves framework behavior before production role graphs are decomposed into checkpointable stages.

## Alternatives

- Custom domain-only JSON snapshots: rejected for losing MAF pending-message/executor semantics.
- Direct `FileCheckpointStorage`: rejected because default permissions and path policy are weaker
  than other repository state stores.
- Add database/Redis now: rejected until local recovery semantics and operational need are measured.

## Consequences and validation

Completed supersteps are not rerun, but side effects inside an interrupted superstep still require
idempotency. Files are not safe to import from untrusted users even with restricted decoding. Unit,
adversarial and real kill/restart tests own these boundaries; OTel and role graph decomposition are
separate Phase J steps.
