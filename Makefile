SHELL := /usr/bin/env bash

UV ?= uv
COMPOSE ?= docker compose

-include .env

CLICKHOUSE_USER ?= agentic
CLICKHOUSE_PASSWORD ?= agentic_dev_only
CLICKHOUSE_CLIENT = $(COMPOSE) exec -T clickhouse clickhouse-client \
	--user "$(CLICKHOUSE_USER)" --password "$(CLICKHOUSE_PASSWORD)"
DBT = $(COMPOSE) run --rm --no-deps dbt

.PHONY: bootstrap lint format-check test check compose-validate \
	platform-up platform-status platform-down seed platform-test \
	clickhouse-test dbt-baseline-test dbt-image dbt-version dbt-debug \
	dbt-parse dbt-compile dbt-build dbt-test

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

platform-up:
	$(COMPOSE) up -d --wait clickhouse

platform-status:
	$(COMPOSE) ps

platform-down:
	$(COMPOSE) down

seed: platform-up
	$(CLICKHOUSE_CLIENT) --multiquery < platform/clickhouse/seed/001_ecommerce.sql
	$(CLICKHOUSE_CLIENT) --multiquery < platform/clickhouse/seed/002_analytics.sql

clickhouse-test: platform-up
	$(CLICKHOUSE_CLIENT) --multiquery < platform/clickhouse/tests/001_smoke.sql

dbt-image:
	$(COMPOSE) build dbt

dbt-version: dbt-image
	$(DBT) --version

dbt-debug: platform-up dbt-image
	$(DBT) debug

dbt-parse: platform-up dbt-image
	$(DBT) parse --no-partial-parse

dbt-compile: platform-up dbt-image
	$(DBT) compile

dbt-build: platform-up dbt-image
	$(DBT) build --full-refresh --fail-fast

dbt-test: platform-up dbt-image
	$(DBT) test --fail-fast

dbt-baseline-test: platform-up
	$(CLICKHOUSE_CLIENT) --multiquery < platform/clickhouse/tests/002_dbt_baseline.sql

platform-test: platform-up dbt-image
	$(CLICKHOUSE_CLIENT) --multiquery < platform/clickhouse/tests/001_smoke.sql
	$(DBT) test --fail-fast
	$(CLICKHOUSE_CLIENT) --multiquery < platform/clickhouse/tests/002_dbt_baseline.sql
