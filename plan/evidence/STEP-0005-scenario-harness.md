# STEP-0005 — Scenario Harness Evidence

Date: 2026-09-05

Status: PASS

## Verified result

`net-revenue` starts from an allowlisted snapshot of source commit `0a6fb5f`. The managed
workspace is `.scenario-state/workspaces/net-revenue`; the main checkout is never reset. Only
`platform/dbt/models/**` and `platform/dbt/tests/**` may drift before public execution. Trusted
baseline records remain outside the agent workspace.

Final reproducibility tuple from two complete reset/seed/dbt-build cycles:

```text
baseline_fingerprint  53bf4b7d8196cfc08bca29171993a6bc0c6b7242e0af21de99b399ae8c638ba9
source_fingerprint    798def11300f3508d037966d38cc1da996414cd37372088b3d480e15c4cf9989
data_fingerprint      3823d7b579969972e9cdd2965d6965895a8581f1a47e9b5156e446d15128b41a
```

The hidden oracle SHA-256 is
`ec93302cc53ace5dece582c773a05d66034232f54f93cd04958b9346dfff6de0`; image ID is
`sha256:c623ae0d5338c3f5fc5f485c0f7abcf732b4009e702ba6cfe8a38eacd8858f18`.
The image contains only the oracle, runs as UID `65532`, mounts submission read-only, drops all
capabilities, has no Docker socket or `API_TOKEN`, and uses an internal network shared only with
fixture ClickHouse. It does not execute submission code.

## Commands and outcomes

- `make scenario-repro-test SCENARIO=net-revenue` — exit `0`; exact tuples matched.
- `make scenario-grade-baseline-test SCENARIO=net-revenue` — exit `0`; contained grader exit `10`,
  JSON `INCOMPLETE` after submission/ClickHouse gates.
- A temporary one-row wrong candidate — schema/invariants passed, business oracle returned `FAIL`;
  it was removed by the next reseed.
- `make platform-test` — exit `0`; Airflow run
  `api_smoke_20260905T183405699692Z_132ccc11`, 11/11 success; dbt 68/68 PASS; SQL PASS.
- `make check` — exit `0`; Ruff, format, 60 pytest checks, Compose validation PASS.
- `git diff --check` — exit `0`.

No GateLLM completion was called. No Docker volume was deleted. Expected baseline grade is not task
success: business PASS remains a Phase F requirement. Residual boundary: maintainers can read the
oracle source; future agents must receive only this snapshot through Phase E policy tools. A
merge-ready Git branch/worktree manager remains Phase D work.
