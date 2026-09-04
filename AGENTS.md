# Repository Guidelines

## Project Structure & Module Organization

This repository is in its design phase. `init/init_build_multi_agent_system.md` defines the MVP architecture; `init/init_cource_plan.md` defines the course. No source, tests, or assets exist yet.

Follow the proposed monorepo layout when scaffolding: orchestration in `orchestrator/`, shared execution code in `runtime/`, roles in `agents/`, typed handoffs in `contracts/`, and authorization in `policies/`. Put data-platform code under `platform/`, evaluation scenarios and graders under `evals/`, and automated checks under `tests/`. Keep deterministic workflow and policy logic out of agent prompts.

## Build, Test, and Development Commands

No `Makefile`, `pyproject.toml`, or runnable services exist yet. For documentation-only changes, run:

```bash
git diff --check       # detect whitespace errors
git status --short     # confirm only intended files changed
```

When scaffolding lands, preserve the designed interface: `uv sync --frozen` for locked dependencies, `pytest` for Python tests, and `make platform-up`, `make seed`, `make dbt-build`, and `make platform-test` for the baseline. For scenarios, run `make scenario-reset SCENARIO=net-revenue`, followed by `scenario-run` and `scenario-grade`.

## Coding Style & Naming Conventions

Write Markdown in UTF-8, keep sections focused, label fenced blocks, and match the edited document's language. Use English identifiers and paths. Target Python 3.12 with four-space indentation, type hints, `snake_case` functions/modules, and `PascalCase` classes and Pydantic models. Pin dependencies in `uv.lock`; avoid floating versions. No formatter or linter is configured yet; add its configuration with the first code scaffold.

For dbt, use `stg_*.sql`, `int_*.sql`, `fct_*.sql`, and `dim_*.sql` in the matching model layers.

## Testing Guidelines

Place tests in `tests/unit`, `tests/integration`, `tests/workflow`, `tests/policy`, or `tests/adversarial`; name Python files `test_<behavior>.py`. Add dbt schema and business tests with model changes. No numeric coverage threshold exists; map every acceptance criterion to reproducible evidence, including regressions and failure paths.

## Commit & Pull Request Guidelines

The repository has no commit history, so no existing convention can be inferred. Use short, imperative Conventional Commit-style subjects, for example `feat(orchestrator): add checkpoint transition` or `docs(init): clarify QA gate`.

PRs should explain the problem and approach, list affected layers, link the issue or task, and include exact validation commands and results. Add screenshots only for UI or dashboard changes. Require independent review; authors must not approve or merge their own changes.
