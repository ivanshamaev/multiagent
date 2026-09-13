# ADR-0023 — PM consumes only accepted requirements handoff

Status: accepted

Date: 2026-09-13

## Context

Before Analyst integration, the PM runtime accepted raw `ContextBundle` input and synthesized a
labelled compatibility analysis. That path was useful while the workflow order was being migrated,
but it bypasses the evidence-backed requirements boundary established by ADR-0022. An LLM could also
erase an Analyst question by returning a confident `ready` specification.

## Decision

PM accepts exactly `PMRequirementsHandoff`, the matching `ANALYSIS_READY` state, and its complete
verified event chain. It receives no workspace context and no tools. Before invoking the model, code
verifies chain integrity, workflow/task identity, accepted TaskRequest and RequirementsAnalysisReport
IDs, distinct actor identity, and the current stage.

`TaskSpecification` gains the typed reason `needs_user`. A `ready` artifact has no blocking reason or
open questions. A blocked artifact has `needs_user` and at least one concrete question. If Analyst
supplied unresolved questions, PM may not return `ready` and its blocked draft must preserve every
question verbatim. These are deterministic boundary rules, not prompt instructions.

The reducer additionally requires the `needs_user` transition reason for a blocked specification.
PM model output cannot provide IDs, timestamps, producer identity, evidence, transition target,
reason, or budget charge. The only model-controlled data is the bounded specification draft.

The frozen, human-authored Data Engineer scenario bootstrap remains separate: it attests a trusted
human specification and does not expose a model-authored shortcut into PM or implementation.

## Consequences

The old scenario-to-PM compatibility request is removed. Live PM validation must first execute the
Analyst pipeline or receive persisted, independently verified handoff/state/events. A workflow that
ends in `BLOCKED/needs_user` cannot be resumed in place because terminal history is immutable; user
clarification needs a later, explicitly modelled workflow. This favors auditability over a hidden
mutation of accepted requirements.
