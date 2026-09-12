# STEP-0010 evidence — read-only QA quality loop

Completed 2026-09-12. ADR-0020 fixes separation of duties. `qa_v1` exposes only bounded reads and
read-only dbt/ClickHouse calls; policy tests reject workspace writes, dbt execution, grader access,
DDL and role mismatch. The model cannot set IDs, authorship, evidence links, budgets or transitions.

## Functional evidence

- Offline integration proves exact `QA FAIL → REWORK → DE write → full validator → QA PASS` order,
  fresh QA sessions and shared rework exhaustion; invalid JSON retains safe call telemetry but no
  report.
- EXP-0003: canonical PASS and 5/5 public-validator-passing mutations rejected by QA; false pass
  0/5. Each assessment used exactly one candidate read and one immutable semantic query.
- Live full loop `quality-net-revenue-20260912161215`: refund-date FAIL, one DE repair, two complete
  validator runs, fresh QA PASS, final `qa_passed`, rework 1/2, 39,466 tokens. Private record:
  `.scenario-state/runs/qa-quality-net-revenue-20260912161215.json`.
- QA found and caused repair of the previously untested nullable ClickHouse `argMax` behavior
  (PRB-0035). An overbroad first repair was rejected by the mandatory validator (PRB-0036).

## Final commands

All commands exited 0:

- `uv run pytest -q tests/integration/test_qa_workflow.py tests/workflow/test_state_machine.py` —
  19 passed; complete focused QA set — 27 passed.
- `make check` — Ruff, format, 280 tests and Compose validation PASS.
- `make mcp-smoke` — authorized read/dbt calls PASS; DDL denied.
- `make scenario-repro-test` — identical baseline/data/source fingerprints.
- `make scenario-grade-baseline-test` — expected isolated `INCOMPLETE` exit contract PASS.
- `make platform-test` — Airflow/Cosmos 11/11, dbt 68/68 and ClickHouse contracts PASS.
- canonical install + `make scenario-run && make scenario-contract-test && make scenario-grade` —
  dbt 78/78, public SQL and all five hidden checks PASS.

Residual risks: one scenario/model snapshot, stochastic schema failures remain possible and closed,
and the Phase G Reviewer gate is not part of STEP-0010.
