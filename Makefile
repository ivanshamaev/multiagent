SHELL := /usr/bin/env bash

UV ?= uv
COMPOSE ?= docker compose

-include .env

CLICKHOUSE_USER ?= agentic
CLICKHOUSE_PASSWORD ?= agentic_dev_only
CLICKHOUSE_CLIENT = $(COMPOSE) exec -T clickhouse clickhouse-client \
	--user "$(CLICKHOUSE_USER)" --password "$(CLICKHOUSE_PASSWORD)"
DBT = $(COMPOSE) run --rm --no-deps dbt
AIRFLOW_API_PORT ?= 8080
AIRFLOW_API_BASE_URL ?= http://127.0.0.1:$(AIRFLOW_API_PORT)
AIRFLOW_ADMIN_USERNAME ?= airflow
AIRFLOW_ADMIN_PASSWORD ?= airflow_dev_only
AIRFLOW_API_REQUEST_TIMEOUT_SECONDS ?= 10
AIRFLOW_API_POLL_TIMEOUT_SECONDS ?= 180
AIRFLOW_API_POLL_INTERVAL_SECONDS ?= 2
export AIRFLOW_API_BASE_URL AIRFLOW_ADMIN_USERNAME AIRFLOW_ADMIN_PASSWORD
export AIRFLOW_API_REQUEST_TIMEOUT_SECONDS AIRFLOW_API_POLL_TIMEOUT_SECONDS
export AIRFLOW_API_POLL_INTERVAL_SECONDS
AIRFLOW = $(COMPOSE) exec -T airflow-scheduler airflow
AIRFLOW_VERSION = $(COMPOSE) run --rm --no-deps --entrypoint airflow airflow-init version

.PHONY: bootstrap lint format-check test check compose-validate \
	clickhouse-up platform-up platform-status platform-down seed platform-test \
	clickhouse-test dbt-baseline-test dbt-image dbt-version dbt-debug \
	dbt-parse dbt-compile dbt-build dbt-test airflow-version airflow-init \
	airflow-up airflow-validate airflow-test

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

platform-up:
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

airflow-version:
	$(AIRFLOW_VERSION)

airflow-init:
	$(COMPOSE) up -d --wait airflow-postgres
	$(COMPOSE) run --rm --no-deps airflow-init

airflow-up:
	$(COMPOSE) up -d --wait --wait-timeout 240 airflow-api-server airflow-scheduler airflow-dag-processor

airflow-validate: airflow-up
	@import_errors="$$( $(AIRFLOW) dags list-import-errors --output=json )" || exit "$$?"; \
		test "$${import_errors}" = "[]" || { \
			printf '%s\n' "$${import_errors}"; \
			exit 1; \
		}
	$(AIRFLOW) dags details ecommerce_hourly --output=json >/dev/null

airflow-test: airflow-validate
	$(UV) run python platform/airflow/scripts/api_smoke.py

platform-test: clickhouse-up dbt-image airflow-test
	$(CLICKHOUSE_CLIENT) --multiquery < platform/clickhouse/tests/001_smoke.sql
	$(DBT) test --fail-fast
	$(CLICKHOUSE_CLIENT) --multiquery < platform/clickhouse/tests/002_dbt_baseline.sql
