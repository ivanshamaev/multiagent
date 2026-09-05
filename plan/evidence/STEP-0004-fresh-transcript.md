# Airflow + Cosmos — fresh gate transcript

All timestamps are UTC. Sensitive values and complete verbose dbt output are intentionally not persisted.

## Build and version gate

```text
Command: make -s airflow-version
Exit: 0
Airflow 3.3.1
pip check (Airflow): No broken requirements found.
Astronomer Cosmos 1.15.0
pip check (dbt venv): No broken requirements found.
dbt Core 1.11.14; clickhouse 1.10.2
Image: sha256:95c7be7e969d2a414d3a43679b779c32443b86ed7f3bc0a597888f64da6772bd
```

The first Cosmos build attempt returned exit `1`: no-deps installation lacked `aenum` and `deprecation`. PRB-0011 records the hash-locked correction; the fresh command above is the accepted result.

## Platform and data readiness

```text
Command: make platform-up
Exit: 0
Result: ClickHouse, PostgreSQL, Airflow API, Scheduler and Dag Processor healthy.

Command: airflow dags list-import-errors --output=json
Exit: 0
Result: []

Command: airflow dags list-runs <each managed DAG> --state running --output=json
Exit: 0
Result: [] for ecommerce_hourly, ecommerce_acceptance and ecommerce_failure_probe.

Command: make seed
Exit: 0
Result: raw and analytics fixtures recreated.

Command: make dbt-build
Exit: 0
Result: 2 tables, 6 views and 68 data tests; PASS=76 WARN=0 ERROR=0.
```

## Positive and negative API gates

```text
Command: make airflow-test
Exit: 0
Result: api_smoke_20260905T175731036564Z_453330f4; 11/11 success; dbt baseline PASS.

Command: make airflow-failure-test
Exit: 0
Result: api_smoke_20260905T175905584317Z_23ea7e57; expected failure; dbt baseline PASS.
Task states: load_raw=success, dbt_tests=failed, publish=upstream_failed.

Command: make airflow-test
Exit: 0
Result: api_smoke_20260905T180008738709Z_00823606; 11/11 success; dbt baseline PASS.

Command: make platform-test
Exit: 0
Result: api_smoke_20260905T180138301267Z_a3908eb5; 11/11 success; raw baseline PASS; dbt PASS=68 WARN=0 ERROR=0; mart baseline PASS.
```

The last positive task-state query reported success for `load_raw`, four `dbt.stg_*_run`, two `dbt.int_*_run`, `dbt.dim_customers_run`, `dbt.fct_orders_run`, `dbt.dbt_test` and `publish`.

## Local and isolation gates

```text
Command: make check
Exit: 0
Result: Ruff PASS; format PASS; pytest 32 passed; Compose validation PASS.

Command: git diff --check
Exit: 0

Command: resolved Compose scan plus API/Scheduler/Dag Processor/ClickHouse/dbt env-presence checks
Exit: 0
Result: API_TOKEN absent; env_file absent; Docker socket absent.
```

Runtime checksum command:

```bash
{ find platform/airflow -type f -not -path '*/__pycache__/*' -print0; printf '%s\0' docker-compose.yml Makefile .env.example; } | sort -z | xargs -0 sha256sum | sha256sum
```

Observed checksum: `4c2cebe9f9761dfef2b7367dd338bb9c5cd1c7d39f634ab20790b90f2ac76f39`.
