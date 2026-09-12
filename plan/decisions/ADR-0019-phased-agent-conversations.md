# ADR-0019 — Phased fresh conversations for bounded agent execution

Status: accepted

Date: 2026-09-12

## Context

The cheapest GateLLM model passing strict schema and function-call probes rejected the third round
of a tool-history conversation with HTTP 400. A monolithic agent also allowed a model-generated
parallel batch to fan out before MAF's best-effort call limit was evaluated. Increasing retries or
prompting cannot turn either behavior into a deterministic boundary.

## Decision

Run the Net Revenue Data Engineer as three fresh, one-tool-round conversations: investigation,
mart SQL implementation, and contract-test implementation. The control plane supplies bounded
content-addressed context, exposes a phase-specific least-privilege tool set, and retains one shared
gateway ledger across all conversations. Each phase requires exactly one evidence record.

The provider forces the initial call, disables parallel tool calls, then lets MAF request one final
response. Tool-history responses omit provider schema mode but remain locally validated against the
closed Pydantic draft. The control plane aggregates every completed model call's usage, latency,
and hashes before reducer accounting. Only the independent validator decides acceptance.

## Alternatives

- Keep one long MAF conversation — rejected by an isolated three-round HTTP 400 reproduction.
- Raise function-call limits — rejected because the limit is evaluated after a parallel batch.
- Remove structured drafts — rejected because unvalidated prose cannot enter domain artifacts.
- Use a materially more expensive model immediately — deferred until the cost-first route has a
  measured phased result.

## Consequences and validation

Fresh phases repeat immutable context and therefore spend more input tokens, but bound provider
history and simplify least privilege. Offline integration must prove three calls, three evidence
records, aggregate usage, isolated writes, reducer transitions, and validator execution. Live runs
must retain terminal metadata and stop on provider rate limits rather than probe around them.
