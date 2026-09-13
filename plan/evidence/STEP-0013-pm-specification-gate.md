# STEP-0013 evidence — PM specification gate

Date: 2026-09-13

Status: PASS

## Delivered boundary

- ADR-0023 removes the compatibility analysis adapter. PM accepts only a matching
  `PMRequirementsHandoff`, `ANALYSIS_READY` state, and complete verified event chain.
- PM receives the task and accepted analysis summary, but no `ContextBundle`, raw evidence body,
  filesystem, dbt, ClickHouse, network, grader, or other tool.
- `SpecificationBlockReason.NEEDS_USER` is contract- and reducer-enforced. A ready specification
  cannot carry questions/reason; a blocked specification requires both. Existing Analyst questions
  cannot be erased, answered by assumption, reordered, or replaced by model output.
- Workflow code owns artifact IDs, actor identity, timestamps, budget charge, target stage, and
  terminal reason. PM controls only the bounded structured draft.
- `runtime.requirements_live` composes the real Analyst and PM workflows and persists only mode-0600
  sanitized metrics under ignored `.scenario-state/runs/`.

## Verification

- Narrow contract/workflow gate — exit 0: 38 tests passed, including ready, needs-user, chain,
  cross-scope, identity, malformed output, budget and prompt-injection cases.
- Final `make check` — exit 0: Ruff, format, Compose validation and 328 tests passed.
- `make requirements-live SCENARIO=net-revenue ANALYST_MODEL=openai/gpt-5.6-luna
  PM_MODEL=openai/gpt-5.6-luna ANALYST_CASE=canonical` — exit 0. Workflow
  `requirements-net-revenue-canonical-05ebaff6e8c8` reached `BLOCKED/needs_user` as expected: 22
  facts, 9 unresolved questions, 3 read-only tools, 4 Analyst calls plus 1 PM call, 17,671 tokens,
  estimated 1.932360 ₽. Private record:
  `.scenario-state/runs/requirements-requirements-net-revenue-canonical-05ebaff6e8c8.json`.
- `make mcp-smoke SCENARIO=net-revenue` — exit 0: three successful permitted calls and expected
  ClickHouse write denial.
- `make scenario-repro-test SCENARIO=net-revenue` — exit 0; baseline, source and data fingerprints
  matched across two resets.
- `make scenario-grade-baseline-test SCENARIO=net-revenue` — exit 0; isolated grader returned the
  expected `INCOMPLETE`.
- `make platform-test` — exit 0; Airflow/Cosmos API graph 11/11, ClickHouse checks and dbt 68/68.
- `git diff --check` — required after documentation update.
- `make platform-down` — exit 0; `docker compose ps` is empty. Named ClickHouse, Airflow log and
  PostgreSQL volumes remain present.

## Residual risks and next step

One live run proves integration, not statistical reliability. The current request correctly blocks
because Analyst has nine material unknowns; the resolved READY path is deterministic and covered
offline, but needs a later user-clarification protocol for live validation. `BLOCKED` is terminal in
v1, so clarification must start an explicitly linked workflow rather than mutate history.

Phase H is complete. STEP-0014 should implement Phase I read-only Airflow MCP over stable `/api/v2`,
starting with DAG/run/task metadata and logs; controlled dev trigger remains a later capability.
