# Repository Guidelines

## Project Structure & Module Organization

This platform underpins a course. `init/` contains proposals, not evidence. Use `plan/development-plan.md` for the roadmap, `plan/steps/` for active work, and `plan/{decisions,problems,evidence}/` for records.

Local control-plane code belongs in `orchestrator/`, `runtime/`, role-specific `agents/`, typed `contracts/`, and deterministic `policies/`. Containerized services and dbt code live in `platform/`. Python tests are grouped under `tests/{unit,integration,workflow,policy,adversarial}`. Keep authorization and workflow transitions in code, not prompts.

## Build, Test, and Development Commands

- `make bootstrap` syncs the Python 3.12 `.venv` from `uv.lock`.
- `make check` runs Ruff, pytest, and Compose validation.
- `make platform-up` starts ClickHouse and Airflow/PostgreSQL, waiting for health.
- `make seed` recreates deterministic `raw` data and resets `analytics`.
- `make dbt-debug`, `make dbt-parse`, and `make dbt-compile` validate dbt configuration and SQL.
- `make dbt-build` builds all models and runs 68 data tests.
- `make airflow-test` validates JWT auth and an 11-task Cosmos/dbt execution graph.
- `make airflow-failure-test` proves a failed dbt test blocks `publish`.
- `make platform-test` combines Airflow, dbt, and independent SQL checks.
- `make platform-down` stops services without deleting volumes.

`ecommerce_hourly` and its manual acceptance twin use Cosmos `DbtTaskGroup`; keep scheduled execution paused unless data readiness is intentional.

## Planning, Evidence, and Testing

Before a nontrivial change, update `plan/steps/STEP-NNNN-short-name.md` with scope, acceptance criteria, risks, and verification. Record architectural choices before implementation. A systematic defect needs reproduction, cause, fix, and regression check. On completion, record exact commands, exit codes, remaining risks, and a compact persistent evidence summary.

Name Python tests `test_<behavior>.py`; every fixed defect needs regression coverage. Keep hidden graders independent from agent-created tests. Never weaken an assertion, fixture, policy, or grader to obtain a pass.

## Coding Style & Security

Use four-space Python indentation, type hints, `snake_case` modules/functions, and `PascalCase` classes. Ruff is authoritative. dbt models use `stg_*.sql`, `int_*.sql`, `fct_*.sql`, or `dim_*.sql`; state each grain and avoid implicit `SELECT *`. Pin dependencies and Docker images.

Keep `.env` ignored. `API_TOKEN` names the GateLLM secret; its value must never enter logs, fixtures, plans, build contexts, or Data Platform containers. Bind exposed services to loopback. Never delete volumes or access production without explicit approval.

## Commit & Pull Request Guidelines

History contains only generic bootstrap commits, so no reliable convention exists yet. Use short imperative subjects such as `feat(platform): add airflow baseline`. PRs must identify the problem, affected layers, linked step, validation evidence, ADR/problem records, and remaining risks. Authors may not approve their own changes.
