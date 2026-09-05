SHELL := /usr/bin/env bash

UV ?= uv
COMPOSE ?= docker compose

-include .env

CLICKHOUSE_USER ?= agentic
CLICKHOUSE_PASSWORD ?= agentic_dev_only
# clickhouse-client reads credentials from the container environment.
CLICKHOUSE_CLIENT = $(COMPOSE) exec -T clickhouse clickhouse-client
DBT = $(COMPOSE) run --rm --no-deps dbt
AIRFLOW_API_PORT ?= 8080
AIRFLOW_API_BASE_URL ?= http://127.0.0.1:$(AIRFLOW_API_PORT)
AIRFLOW_ADMIN_USERNAME ?= airflow
AIRFLOW_ADMIN_PASSWORD ?= airflow_dev_only
AIRFLOW_API_REQUEST_TIMEOUT_SECONDS ?= 10
AIRFLOW_API_POLL_TIMEOUT_SECONDS ?= 300
AIRFLOW_API_POLL_INTERVAL_SECONDS ?= 2
export AIRFLOW_API_BASE_URL AIRFLOW_ADMIN_USERNAME AIRFLOW_ADMIN_PASSWORD
export AIRFLOW_API_REQUEST_TIMEOUT_SECONDS AIRFLOW_API_POLL_TIMEOUT_SECONDS
export AIRFLOW_API_POLL_INTERVAL_SECONDS
AIRFLOW = $(COMPOSE) exec -T airflow-scheduler airflow
AIRFLOW_VERSION = $(COMPOSE) run --rm --no-deps --entrypoint airflow airflow-init version
SCENARIO ?= net-revenue
SCENARIO_HARNESS = $(UV) run python -m runtime.scenario_harness
SCENARIO_WORKSPACE = $(abspath .scenario-state/workspaces/$(SCENARIO))
SCENARIO_DBT_PROJECT = $(SCENARIO_WORKSPACE)/platform/dbt
SCENARIO_GRADER = SCENARIO_WORKSPACE_PATH="$(SCENARIO_WORKSPACE)" \
	$(COMPOSE) run --rm --no-deps scenario-grader

.PHONY: bootstrap lint format-check test check compose-validate \
	clickhouse-up platform-up platform-status platform-down seed platform-test \
	clickhouse-test dbt-baseline-test dbt-image dbt-version dbt-debug \
	dbt-parse dbt-compile dbt-build dbt-test airflow-version airflow-init \
	airflow-image airflow-up airflow-validate airflow-test airflow-failure-test \
	scenario-init scenario-reset scenario-status scenario-verify scenario-fingerprint \
	scenario-baseline-build scenario-run scenario-grader-image scenario-grade \
	scenario-grade-baseline-test scenario-repro-test scenario-test

bootstrap:
	$(UV) sync --frozen

lint:
	$(UV) run ruff check .

format-check:
	$(UV) run ruff format --check .

test:
	$(UV) run pytest

compose-validate:
	$(COMPOSE) config --quiet

check: lint format-check test compose-validate

clickhouse-up:
	$(COMPOSE) up -d --wait clickhouse

platform-up: airflow-image
	$(COMPOSE) up -d --wait --wait-timeout 240 clickhouse airflow-api-server airflow-scheduler airflow-dag-processor

platform-status:
	$(COMPOSE) ps

platform-down:
	$(COMPOSE) down

seed: clickhouse-up
	$(CLICKHOUSE_CLIENT) --multiquery < platform/clickhouse/seed/001_ecommerce.sql
	$(CLICKHOUSE_CLIENT) --multiquery < platform/clickhouse/seed/002_analytics.sql

clickhouse-test: clickhouse-up
	$(CLICKHOUSE_CLIENT) --multiquery < platform/clickhouse/tests/001_smoke.sql

dbt-image:
	$(COMPOSE) build dbt

dbt-version: dbt-image
	$(DBT) --version

dbt-debug: clickhouse-up dbt-image
	$(DBT) debug

dbt-parse: clickhouse-up dbt-image
	$(DBT) parse --no-partial-parse

dbt-compile: clickhouse-up dbt-image
	$(DBT) compile

dbt-build: clickhouse-up dbt-image
	$(DBT) build --full-refresh --fail-fast

dbt-test: clickhouse-up dbt-image
	$(DBT) test --fail-fast

dbt-baseline-test: clickhouse-up
	$(CLICKHOUSE_CLIENT) --multiquery < platform/clickhouse/tests/002_dbt_baseline.sql

airflow-image:
	$(COMPOSE) build airflow-init

airflow-version: airflow-image
	$(AIRFLOW_VERSION)
	$(COMPOSE) run --rm --no-deps --entrypoint bash airflow-init -c \
		'python -m pip check && python -c "import cosmos; print(cosmos.__version__)" && /opt/airflow/dbt-venv/bin/python -m pip check && /opt/airflow/dbt-venv/bin/dbt --version'

airflow-init: airflow-image
	$(COMPOSE) up -d --wait airflow-postgres
	$(COMPOSE) run --rm --no-deps airflow-init

airflow-up: airflow-image
	$(COMPOSE) up -d --wait --wait-timeout 240 airflow-api-server airflow-scheduler airflow-dag-processor

airflow-validate: airflow-up
	@import_errors="$$( $(AIRFLOW) dags list-import-errors --output=json )" || exit "$$?"; \
		test "$${import_errors}" = "[]" || { \
			printf '%s\n' "$${import_errors}"; \
			exit 1; \
		}
	$(AIRFLOW) dags details ecommerce_hourly --output=json >/dev/null
	$(AIRFLOW) dags details ecommerce_acceptance --output=json >/dev/null
	$(AIRFLOW) dags details ecommerce_failure_probe --output=json >/dev/null

airflow-test: airflow-validate
	$(UV) run python platform/airflow/scripts/api_smoke.py
	$(CLICKHOUSE_CLIENT) --multiquery < platform/clickhouse/tests/002_dbt_baseline.sql

airflow-failure-test: airflow-validate
	$(UV) run python platform/airflow/scripts/api_smoke.py --expect-failure
	$(CLICKHOUSE_CLIENT) --multiquery < platform/clickhouse/tests/002_dbt_baseline.sql

platform-test: clickhouse-up dbt-image airflow-test
	$(CLICKHOUSE_CLIENT) --multiquery < platform/clickhouse/tests/001_smoke.sql
	$(DBT) test --fail-fast
	$(CLICKHOUSE_CLIENT) --multiquery < platform/clickhouse/tests/002_dbt_baseline.sql

scenario-init:
	$(SCENARIO_HARNESS) reset --scenario "$(SCENARIO)"

scenario-verify:
	$(SCENARIO_HARNESS) verify --scenario "$(SCENARIO)"

scenario-status:
	$(SCENARIO_HARNESS) status --scenario "$(SCENARIO)"

scenario-fingerprint:
	$(SCENARIO_HARNESS) fingerprint --scenario "$(SCENARIO)"

scenario-baseline-build: scenario-verify clickhouse-up dbt-image
	DBT_PROJECT_PATH="$(SCENARIO_DBT_PROJECT)" $(DBT) build --full-refresh --fail-fast
	$(CLICKHOUSE_CLIENT) --multiquery < platform/clickhouse/tests/002_dbt_baseline.sql

scenario-reset: scenario-init
	$(MAKE) --no-print-directory seed
	$(MAKE) --no-print-directory scenario-baseline-build SCENARIO="$(SCENARIO)"
	@set -o pipefail; \
		$(CLICKHOUSE_CLIENT) --multiquery \
			< platform/clickhouse/tests/003_scenario_fingerprint.sql \
		| $(SCENARIO_HARNESS) record-data --scenario "$(SCENARIO)"

scenario-run: scenario-verify clickhouse-up dbt-image
	DBT_PROJECT_PATH="$(SCENARIO_DBT_PROJECT)" $(DBT) build --full-refresh --fail-fast
	$(CLICKHOUSE_CLIENT) --multiquery < platform/clickhouse/tests/001_smoke.sql

scenario-grader-image:
	$(COMPOSE) build scenario-grader

scenario-grade: scenario-verify clickhouse-up scenario-grader-image
	$(SCENARIO_HARNESS) verify-oracle --scenario "$(SCENARIO)"
	$(SCENARIO_GRADER)

scenario-grade-baseline-test: scenario-verify clickhouse-up scenario-grader-image
	$(SCENARIO_HARNESS) verify-oracle --scenario "$(SCENARIO)"
	@set +e; output="$$( $(SCENARIO_GRADER) 2>&1 )"; status="$$?"; set -e; \
		printf '%s\n' "$$output"; \
		test "$$status" -eq 10 || { \
			printf 'expected baseline grader exit 10, received %s\n' "$$status" >&2; \
			exit 1; \
		}

scenario-repro-test:
	@first="$$( \
		$(MAKE) --no-print-directory -s scenario-reset SCENARIO="$(SCENARIO)" >/dev/null \
		&& $(SCENARIO_HARNESS) fingerprint --scenario "$(SCENARIO)" \
	)"; \
	second="$$( \
		$(MAKE) --no-print-directory -s scenario-reset SCENARIO="$(SCENARIO)" >/dev/null \
		&& $(SCENARIO_HARNESS) fingerprint --scenario "$(SCENARIO)" \
	)"; \
	test "$$first" = "$$second" || { \
		printf 'first:  %s\nsecond: %s\n' "$$first" "$$second" >&2; \
		exit 1; \
	}; \
	printf '%s\n' "$$second"

scenario-test: scenario-repro-test
	$(MAKE) --no-print-directory scenario-grade-baseline-test SCENARIO="$(SCENARIO)"
