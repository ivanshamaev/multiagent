# ADR-0020 — Independent read-only QA boundary

Status: accepted

Date: 2026-09-12

## Context

Public validation proves build, schema, repository policy, and a bounded SQL contract, but one of
ten STEP-0009 candidates passed those gates and still failed the hidden business oracle. Reusing
the Data Engineer identity, write tools, or hidden diagnostics for QA would turn review into
self-approval or leak evaluation evidence into implementation.

## Decision

QA is a distinct actor and capability profile. It starts only from `VALIDATED`, receives the frozen
specification plus a content-addressed candidate context, and may use workspace reads and bounded
read-only ClickHouse/dbt inspection only. It has no write, shell, grader, secret, or production
capability. Fresh inspection and probe conversations share one QA gateway ledger.

The model emits only a minimal draft decision and defect explanation. The control plane creates
identity, authorship, evidence references, checks, defects, resource charges, and transitions. A QA
failure consumes one shared workflow rework attempt. The Data Engineer may repair only from public
QA evidence; the candidate must then pass the complete deterministic validator before QA can run
again. Hidden grading remains evaluation-only and never becomes repair context.

Mutation fixtures are authored independently of model output and retained outside the agent
workspace. They measure false pass and false defect rates; they do not modify QA prompts or weaken
validator/grader assertions after observing a run.

## Alternatives

- Let DE perform its own QA — rejected because separation of duties would be cosmetic.
- Treat QA prose as evidence — rejected because observations must bind to measured tool outputs.
- Feed hidden grader failures to QA or DE — rejected because it leaks the oracle.
- Skip validator after QA-driven repair — rejected because write access invalidates prior evidence.
- Combine Reviewer approval with QA — deferred so defect detection and maintainability approval can
  be measured independently.

## Consequences and validation

QA can discover semantic problems missed by public gates without gaining implementation authority.
Extra model/tool cost is separately measurable and remains under the workflow budget. Tests must
prove role/profile isolation, exact evidence ownership, fail-closed invalid drafts, shared rework
exhaustion, and the mandatory `DE repair → validator → QA` ordering.
