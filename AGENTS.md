# Repository Guidelines

## Project Structure & Module Organization

`init/` contains proposals, not evidence. `plan/` holds steps, decisions, problems, experiments,
evidence, and progress; follow `Claude.md`.

Control-plane code belongs in `orchestrator/`, `runtime/`, `agents/`, `contracts/`, and `policies/`.
Services/dbt live in `platform/`; MCP packaging in `mcp/`; scenarios and the isolated oracle in
`scenarios/` and `grader/`. Tests use
`tests/{unit,integration,workflow,policy,adversarial}`. Keep authorization in code, not prompts.

## Build, Test, and Development Commands

- `make bootstrap` syncs the Python 3.12 `.venv`.
- `make check` runs Ruff, pytest, plan lint, and Compose validation.
- `make dbt-build` builds models and runs 68 data tests.
- `make airflow-test` validates JWT auth and an 11-task Cosmos/dbt execution graph.
- `make platform-test` combines Airflow, dbt, and independent SQL checks.
- `make mcp-smoke` validates bounded ClickHouse/dbt tools and denial behavior.
- `make scenario-reset` recreates the disposable Net Revenue baseline.
- `make scenario-run` builds a candidate; `make scenario-grade` invokes the isolated grader.
- `make checkpoint-smoke` proves process-kill recovery from a durable MAF checkpoint.
- `make role-pipeline-test` proves typed rework and receipt-backed restart.
- `make telemetry-test` proves the content-free trace contract; `make observability-smoke` proves
  Collector sampling/metrics, Tempo retention, Prometheus, and the provisioned Grafana dashboard.
- `make runner-isolation-test` proves per-role Bubblewrap UID/filesystem/network isolation and
  request-bound MCP authentication.
- `make platform-down` and `make observability-down` stop services without deleting volumes.

## Planning, Evidence, and Testing

Before a nontrivial change, update `plan/steps/STEP-NNNN-short-name.md` with scope, acceptance,
risks, and verification. Record architecture first. A systematic defect needs reproduction, cause,
fix, and regression coverage. On completion, record commands, exit codes, risks, and evidence.

Name Python tests `test_<behavior>.py`; defects need regression coverage. Keep hidden graders independent. Never weaken assertions for a pass.

## Coding Style & Security

Use four-space Python indentation, type hints, `snake_case` modules/functions, and `PascalCase` classes. Ruff is authoritative. dbt models use `stg_*.sql`, `int_*.sql`, `fct_*.sql`, or `dim_*.sql`; state each grain and avoid implicit `SELECT *`. Pin dependencies and Docker images.

Keep `.env` ignored. `API_TOKEN` must never enter logs, plans, images, or Data Platform containers. Bind services to loopback. Never delete volumes or access production without approval. Role
sandboxes must fail if Bubblewrap/user namespaces are unavailable; never add an unsandboxed
fallback. MCP signing keys remain under owner-only `.scenario-state/mcp-auth/`.

## Commit & Pull Request Guidelines

Use short imperative subjects such as `feat(platform): add airflow baseline`. PRs identify the
problem, affected layers, linked step, validation evidence, ADR/problem records, and remaining
risks. Authors may not approve their own changes.
