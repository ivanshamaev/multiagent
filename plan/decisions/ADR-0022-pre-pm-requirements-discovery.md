# ADR-0022 — Analyst discovery precedes PM specification

Status: accepted

Date: 2026-09-13

## Context

The original workflow asked PM to finalize semantics before an agent had inspected available data.
Its later `AnalysisReport` was produced by Data Engineer and therefore mixed requirements discovery
with implementation analysis. That ordering cannot reliably expose missing sources, incompatible
grains, or semantic ambiguity before the specification gate.

## Decision

The canonical order is `CREATED → ANALYZING → ANALYSIS_READY → SPECIFYING → SPEC_READY | BLOCKED`.
`ANALYSIS_READY` accepts a new `RequirementsAnalysisReport`; the existing `AnalysisReport` remains a
version-one technical implementation artifact and is no longer a requirements gate. This explicit
type split avoids silently changing the meaning of serialized artifacts.

Analyst owns evidence-backed observations about schemas, dbt nodes, lineage, profiles, assumptions,
risks, and unresolved questions. PM owns business semantics and the `TaskSpecification` decision.
The reducer alone owns readiness transitions. An analysis may be accepted with open questions; the
later PM gate must resolve them or return `BLOCKED` with `needs_user` as its typed reason.

Every factual or lineage claim references successful, same-task retained evidence. Code creates
artifact, claim, and evidence identities. The model may propose bounded probes and interpretations,
but cannot write, run DDL/DML, select production databases, expose secrets, or choose workflow state.
PM handoff validation binds the original request and accepted report to one workflow and a verified
configuration fingerprint.

The first implementation uses code-owned SQL for profiling. Although the shared AST policy also
rejects unsafe model-authored SQL, exposing arbitrary SQL generation adds no value to the current
fixed discovery probe, so the Analyst phase receives a zero-argument facade instead.

Existing frozen human specifications used by the autonomous implementation scenario enter through a
separate trusted bootstrap adapter until PM integration is migrated in STEP-0013. This compatibility
adapter may not be used for an unapproved model-authored specification.

## Consequences

Tests and factories must use the pre-PM order and prove that direct `CREATED → SPECIFYING` and
`ANALYSIS_READY → IMPLEMENTING` are rejected. Analyst gets a dedicated least-privilege profile and
fresh bounded phases. STEP-0013 will change the PM runtime to consume the typed handoff; it must not
reintroduce raw workspace discovery or treat assumptions as facts.
