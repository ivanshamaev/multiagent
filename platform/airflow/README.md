# Airflow baseline

This directory contains the active Airflow 3 DAG bundle. The Compose stack uses
PostgreSQL state, `LocalExecutor`, an API Server, Scheduler and Dag Processor.
The public API is bound to `127.0.0.1:8080`; PostgreSQL is internal-only.

`ecommerce_hourly` uses Astronomer Cosmos to render and execute the dbt lineage:
four staging models, two intermediate models, two marts and an `AFTER_ALL` test
gate. dbt runs from an isolated virtualenv; no Docker socket is mounted. The
manual `ecommerce_acceptance` DAG shares this graph and avoids enabling the
hourly schedule during tests. `ecommerce_failure_probe` proves that a failing
Cosmos test prevents `publish`.

Use the repository interface:

```bash
make airflow-version
make airflow-up
make airflow-validate
make airflow-test
make airflow-failure-test
```

Authentication uses a local-development FAB user and JWT from `/auth/token`.
Never print or persist the password or returned token. Configuration from
`.env` is interpolated through an explicit Compose allowlist; `API_TOKEN` is not
passed to any Data Platform container.
