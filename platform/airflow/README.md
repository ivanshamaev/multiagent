# Airflow baseline

This directory contains the active Airflow 3 DAG bundle. The Compose stack uses
PostgreSQL state, `LocalExecutor`, an API Server, Scheduler and Dag Processor.
The public API is bound to `127.0.0.1:8080`; PostgreSQL is internal-only.

`ecommerce_hourly` is currently an executable orchestration contract. Its six
Task SDK tasks validate dependency order and task execution, but do **not** run
the ClickHouse seed or dbt commands yet. Connecting a separate dbt runner is a
later change; mounting the Docker socket is not an accepted implementation.

Use the repository interface:

```bash
make airflow-version
make airflow-up
make airflow-validate
make airflow-test
```

Authentication uses a local-development FAB user and JWT from `/auth/token`.
Never print or persist the password or returned token. Configuration from
`.env` is interpolated through an explicit Compose allowlist; `API_TOKEN` is not
passed to any Data Platform container.
