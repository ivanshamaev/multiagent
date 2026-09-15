# ADR-0033 — Two-layer evaluation benchmark

Status: accepted

Date: 2026-09-14

## Context

Agent quality is stochastic and paid, while control-plane, safety and recovery invariants must run
on every change. Treating unit tests as model-quality evidence is false confidence; running ten live
LLM attempts on every commit is slow, costly and rate-limit-sensitive. Existing steps already hold
provenanced live samples for DE, Analyst, QA, PM and Reviewer.

## Decision

Phase K has two explicit layers:

1. A versioned offline regression suite repeatedly launches repository-owned pytest node IDs in
   fresh sanitized processes. It measures reliability, quality-gate and safety invariants against a
   strict committed threshold baseline and emits a content-addressed typed report.
2. A historical live baseline indexes already completed model experiments, their fingerprints,
   run counts, task/false-pass rates, tokens, latency and cost. It is never relabelled as a current
   run. Any future prompt/model/tool change requires a fresh explicitly authorized live sample and
   comparison under the same scenario baseline.

The runner accepts no commands from the manifest, only bounded pytest node IDs under `tests/`.
Configuration fingerprint covers suite, baseline and the code/prompt/policy/scenario inputs. Offline
pass thresholds are 100%; safety failures count as policy violations. Latency is reported but not a
hard correctness threshold because shared-host scheduling is not an agent regression.

## Alternatives

- Live-only benchmark: rejected because infrastructure/rate/cost noise would block ordinary CI.
- Offline-only claims about model quality: rejected because deterministic fakes cannot measure LLM
  reasoning, false passes or cost.
- External eval SaaS: deferred; it expands secret/data/network boundaries without current need.
- Free-form shell benchmark manifest: rejected as a code-execution and scope-expansion surface.

## Consequences

Phase K yields fast reproducible regression evidence and honest separation of current offline
invariants from dated live quality. It does not claim that old model rates apply to a changed
configuration. Reports remain local and content-free; the committed baseline can only be changed by
reviewing a new ADR/step and cannot be auto-updated after failure.
