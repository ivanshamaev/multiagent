# ADR-0018 — Autonomous Data Engineer control-plane ownership

Status: accepted

Date: 2026-09-11

## Context

The first autonomous milestone lets an LLM inspect data, edit dbt files, and request validation.
The model is therefore both useful and untrusted: it must not redefine Net Revenue, choose its own
identity, weaken tests, approve its implementation, or reset resource accounting. STEP-0008 has
safe adapters, but workspace and MCP usage still need one task-scoped budget in the autonomous run.

## Decision

The human-authored Net Revenue specification is a frozen, versioned Pydantic envelope included in
the scenario snapshot. It binds scenario/version, the SHA-256 of `TASK.md`, and a ready
`TaskSpecification` whose IDs, producer, and timestamp are fixed outside the model. Workspace
verification makes the copied specification a protected input.

The Data Engineer may return draft reasoning and request only profile-exposed tools. A local
task-scoped facade creates request IDs and records all workspace/MCP outcomes. One code-owned ledger
serializes calls and accounts for tool count, elapsed time, and retained output before another call
is authorized. Invalid arguments or policy denials terminate the MAF loop loudly.

Only the control plane assembles `AnalysisReport` and `ImplementationResult`, attaches measured
evidence, creates transition commands, and charges model/tool usage. An independent deterministic
validator runs after implementation. Its evidence—not agent prose—selects `VALIDATED`, `REWORK`, or
`FAILED` through the existing reducer. Hidden-grader details and output are never prompt context;
only the external pass/fail metric is retained for evaluation.

## Alternatives

- Let the model emit the complete domain artifacts — rejected because identity, evidence, and
  transition fields would be self-asserted.
- Treat dbt success returned by MCP as final validation — rejected because the agent controls the
  files and can weaken its own tests.
- Separate budgets per adapter — rejected because mixed workspace/MCP calls could exceed the task
  limit while each local counter remained valid.
- Feed hidden-grader diagnostics into repair prompts — rejected because it leaks the oracle and
  turns evaluation into test overfitting.

## Consequences and validation

The autonomous executor remains replaceable and cannot bypass the pure reducer. Rework may improve
an implementation only from public deterministic validator evidence and is bounded by the manifest.
Tests must prove specification tamper detection, cross-adapter cumulative budgets, protected writes,
validator independence, and terminal failure after rework exhaustion.
