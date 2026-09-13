# STEP-0013 — PM specification gate

Status: complete

Owner: primary agent

Started: 2026-09-13

Completed: 2026-09-13

Evidence: `plan/evidence/STEP-0013-pm-specification-gate.md`

Date: 2026-09-13

## Goal

Complete Phase H by placing a tool-free Product Manager Agent after the accepted Analyst handoff.
The gate must either emit a complete, reducer-accepted `TaskSpecification` or terminate with a
typed `needs_user` result. It must never recreate discovery from raw workspace context.

## Scope

- Replace the temporary PM compatibility adapter with input bound to `PMRequirementsHandoff`, the
  current `WorkflowState`, and its verified append-only event chain.
- Add a typed specification blocking reason and enforce its relationship to the decision.
- Keep IDs, actor identity, time, budget accounting, and transitions code-owned.
- Give PM no tools and only the original task plus accepted Analyst facts, assumptions, risks,
  recommendations, and unresolved questions.
- Require every Analyst unresolved question to survive verbatim in a blocked specification; reject
  a `ready` answer while any such question remains.
- Migrate the live smoke path to the real `Analyst → PM` pipeline and persist only sanitized metrics.

## Non-goals

- Collecting or interpreting a user's clarification response.
- Resuming a terminal blocked workflow.
- Changing Analyst probes, Data Engineer execution, or the frozen human-spec scenario bootstrap.
- Giving PM direct dbt, ClickHouse, filesystem, network, or grader access.

## Implementation sequence

1. Record the trust-boundary decision in ADR-0023.
2. Extend `TaskSpecification` with `SpecificationBlockReason.NEEDS_USER` and strengthen reducer
   validation for the PM blocked branch.
3. Rewrite `runtime/agent_runtime.py` around accepted handoff/state/events; remove context discovery
   and scenario request preparation.
4. Update PM instructions so observations, assumptions, and business decisions remain distinct.
5. Add unit/workflow/adversarial coverage for ready, needs-user, omitted questions, forged state,
   cross-task input, identity collision, invalid model output, event replay, and budget overflow.
6. Replace the legacy paid smoke with a composed Analyst-to-PM command and add a Make target.
7. Run narrow tests, full offline gates, one live canonical pipeline, and platform regression.
8. Save exact evidence, update progress/current-status documentation, and stop Docker services without
   deleting volumes.

## Acceptance criteria

- No production PM path can construct a compatibility analysis or accept `ContextBundle` directly.
- PM invocation occurs only at `ANALYSIS_READY` after `verify_event_chain` succeeds and the accepted
  report ID is present in state.
- A handoff with unresolved questions cannot reach `SPEC_READY`; the accepted blocked artifact uses
  `needs_user` and preserves all questions exactly.
- A fully resolved handoff can produce a contract-valid `ready` specification and reach `SPEC_READY`.
- PM has zero tools and one bounded structured model call; measured tokens/time are reducer-charged.
- Cross-task, cross-workflow, forged-artifact, identity-collision, malformed-output, and budget cases
  fail closed with regression tests.
- `make check`, MCP/scenario/platform gates, and a live GateLLM run pass; evidence contains no token,
  prompt body, raw tool output, or sensitive data.

## Risks and mitigations

- **PM silently answers Analyst questions:** deterministic acceptance rejects `ready` and requires
  exact question preservation whenever the handoff is unresolved.
- **Forged handoff beside valid state:** validate task/workflow/artifact IDs and replay the complete
  event chain before any paid call.
- **Prompt injection via facts:** mark all handoff content as untrusted; prompts cannot grant tools or
  control identity/transitions.
- **Terminal clarification:** `BLOCKED` remains terminal in v1. A later step must model a new request
  or explicit clarification workflow instead of mutating history.
- **Cost:** use the configured low-cost reasoning model, one PM call, bounded output, and recorded
  token/cost metadata.

## Planned verification

```bash
uv run pytest -q tests/unit/test_contracts.py tests/workflow/test_state_machine.py
uv run pytest -q tests/workflow/test_agent_runtime.py tests/adversarial
uv run ruff check contracts orchestrator runtime tests
uv run ruff format --check contracts orchestrator runtime tests
make requirements-live PM_MODEL=openai/gpt-5.6-luna ANALYST_CASE=canonical
make check
make mcp-smoke
make scenario-repro-test
make scenario-grade-baseline-test
make platform-test
git diff --check
make platform-down
```
