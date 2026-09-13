# Repository Guidelines

## Project Structure & Module Organization

`init/` contains proposals, not evidence. `plan/` holds the roadmap, steps, decisions, problems,
experiments, evidence, and progress; follow the fuller workflow in `Claude.md`.

Control-plane code belongs in `orchestrator/`, `runtime/`, `agents/`, `contracts/`, and `policies/`.
Services/dbt live in `platform/`; MCP packaging in `mcp/`; scenarios and the isolated oracle in
`scenarios/` and `grader/`. Tests use
`tests/{unit,integration,workflow,policy,adversarial}`. Keep authorization in code, not prompts.

## Build, Test, and Development Commands

- `make bootstrap` syncs Python 3.12 `.venv` from `uv.lock`.
- `make check` runs Ruff, pytest, plan lint, and Compose validation.
- `make platform-up` starts the Data Platform.
- `make dbt-build` builds models and runs 68 data tests.
- `make airflow-test` validates JWT auth and an 11-task Cosmos/dbt execution graph.
- `make platform-test` combines Airflow, dbt, and independent SQL checks.
- `make mcp-smoke` validates bounded ClickHouse/dbt tools and denial behavior.
- `make airflow-mcp-smoke` checks the observer; `make airflow-trigger-smoke` checks the separate
  approved/idempotent dev-DAG trigger.
- `make scenario-reset` recreates the disposable Net Revenue baseline.
- `make scenario-run` builds a candidate; `make scenario-contract-test` runs independent SQL;
  `make scenario-grade` invokes the isolated grader.
- `make scenario-repro-test` and `make scenario-grade-baseline-test` validate isolation boundaries.
- `make checkpoint-smoke` proves process-kill recovery from a durable MAF checkpoint.
- `make role-pipeline-test` proves typed six-role checkpoints and restart after Data Engineer.
- `make platform-down` stops services without deleting volumes.

Keep scheduled `ecommerce_hourly` paused unless data readiness is intentional.

## Planning, Evidence, and Testing

Before a nontrivial change, update `plan/steps/STEP-NNNN-short-name.md` with scope, acceptance criteria, risks, and verification. Record architectural choices before implementation. A systematic defect needs reproduction, cause, fix, and regression check. On completion, record exact commands, exit codes, remaining risks, and a compact persistent evidence summary.

Name Python tests `test_<behavior>.py`; every defect needs regression coverage. Keep hidden graders independent from agent-created tests. Never weaken assertions to obtain a pass.

## Coding Style & Security

Use four-space Python indentation, type hints, `snake_case` modules/functions, and `PascalCase` classes. Ruff is authoritative. dbt models use `stg_*.sql`, `int_*.sql`, `fct_*.sql`, or `dim_*.sql`; state each grain and avoid implicit `SELECT *`. Pin dependencies and Docker images.

Keep `.env` ignored. `API_TOKEN` must never enter logs, plans, images, or Data Platform containers. Bind services to loopback. Never delete volumes or access production without approval.

## Commit & Pull Request Guidelines

History contains only generic bootstrap commits, so no reliable convention exists yet. Use short imperative subjects such as `feat(platform): add airflow baseline`. PRs must identify the problem, affected layers, linked step, validation evidence, ADR/problem records, and remaining risks. Authors may not approve their own changes.
