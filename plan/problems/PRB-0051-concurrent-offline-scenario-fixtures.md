# PRB-0051 — Concurrent offline scenario fixtures

Status: resolved

Date: 2026-09-15

## Reproduction and cause

Running `make check` alongside `make evaluation-benchmark` caused
`test_mutation_installer_changes_only_disposable_candidate[refund-date]` to fail:
another pytest process recreated the same `.scenario-state/workspaces/net-revenue` while the
installer atomically replaced its SQL test. The first check exited 2 (449 PASS, one failure).
This is a shared-fixture race, not a SQL/model defect.

## Fix and regression

`make test` and `make evaluation-benchmark` hold the same repository-local `flock` throughout
execution. The Makefile is fingerprinted. Direct pytest/scenario-mutating commands must not overlap
the benchmark. Repeat both benchmark samples and the full check through these locked targets;
record final results in STEP-0024 evidence. `test_suite_accepts_only_pytest_nodes_not_commands`
also asserts both targets retain the common lock. Assertions and scenario behavior are unchanged.
