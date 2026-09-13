# ADR-0026 — Accept pinned upstream HTTPX2 dependency

Status: accepted

Date: 2026-09-13

## Context

The audit classified `httpx2==2.12.0` as a possible typosquatting risk because it transports the
GateLLM bearer token. Local package metadata and the dependency graph show that OpenAI 3.8.0
requires it and identifies `github.com/pydantic/httpx2` as its source. The Pydantic project describes
HTTPX2 as its maintained continuation of HTTPX; OpenAI's own migration document explicitly uses it.

## Decision

Retain HTTPX2 while the pinned OpenAI/MAF stack requires it. Keep it an explicit exact dependency
with sdist/wheel hashes in `uv.lock`, accept packages only from the configured package index, and
exercise authenticated requests through a fake transport. Re-evaluate provenance on every OpenAI
or MAF upgrade; do not silently substitute a second transport beneath the SDK.

## Alternatives

- Downgrade OpenAI/MAF: rejected because it abandons the validated runtime for an unmeasured stack.
- Add legacy HTTPX for repository calls: rejected because the bearer token would still traverse
  HTTPX2 inside OpenAI and a second client expands the supply chain.
- Replace the SDK with custom HTTP: deferred; it would duplicate retry/schema/tool semantics.

## Consequences and validation

The dependency remains security-sensitive, but it is verified upstream rather than an unexplained
look-alike. Hash locking limits artifact drift, not maintainer compromise. `uv tree --invert
--package httpx2`, installed metadata, provider tests and lock-policy tests form the local gate.
