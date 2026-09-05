# Airflow baseline — fresh gate transcript

All timestamps are UTC. Gate captures uncommitted runtime configuration; source fingerprint covers platform/airflow, Compose, Makefile and .env.example (never .env).

## make -s airflow-version

Started: 2026-09-05T03:57:08Z
Ended: 2026-09-05T03:57:18Z
Exit code: 0

```text
3.3.1
```

## make -s platform-up

Started: 2026-09-05T03:57:18Z
Ended: 2026-09-05T03:58:46Z
Exit code: 0

```text
 Container agentic-data-platform-airflow-postgres-1  Running
 Container agentic-data-platform-clickhouse-1  Running
 Container agentic-data-platform-airflow-init-1  Recreate
 Container agentic-data-platform-airflow-init-1  Recreated
 Container agentic-data-platform-airflow-api-server-1  Recreate
 Container agentic-data-platform-airflow-dag-processor-1  Recreate
 Container agentic-data-platform-airflow-dag-processor-1  Recreated
 Container agentic-data-platform-airflow-api-server-1  Recreated
 Container agentic-data-platform-airflow-scheduler-1  Recreate
 Container agentic-data-platform-airflow-scheduler-1  Recreated
 Container agentic-data-platform-airflow-postgres-1  Waiting
 Container agentic-data-platform-airflow-postgres-1  Healthy
 Container agentic-data-platform-airflow-init-1  Starting
 Container agentic-data-platform-airflow-init-1  Started
 Container agentic-data-platform-airflow-init-1  Waiting
 Container agentic-data-platform-airflow-postgres-1  Waiting
 Container agentic-data-platform-airflow-init-1  Waiting
 Container agentic-data-platform-airflow-postgres-1  Waiting
 Container agentic-data-platform-airflow-postgres-1  Healthy
 Container agentic-data-platform-airflow-postgres-1  Healthy
 Container agentic-data-platform-airflow-init-1  Exited
 Container agentic-data-platform-airflow-dag-processor-1  Starting
 Container agentic-data-platform-airflow-init-1  Exited
 Container agentic-data-platform-airflow-api-server-1  Starting
 Container agentic-data-platform-airflow-api-server-1  Started
 Container agentic-data-platform-airflow-api-server-1  Waiting
 Container agentic-data-platform-airflow-postgres-1  Waiting
 Container agentic-data-platform-airflow-init-1  Waiting
 Container agentic-data-platform-airflow-dag-processor-1  Started
 Container agentic-data-platform-airflow-init-1  Exited
 Container agentic-data-platform-airflow-postgres-1  Healthy
 Container agentic-data-platform-airflow-api-server-1  Healthy
 Container agentic-data-platform-airflow-scheduler-1  Starting
 Container agentic-data-platform-airflow-scheduler-1  Started
 Container agentic-data-platform-airflow-api-server-1  Waiting
 Container agentic-data-platform-airflow-scheduler-1  Waiting
 Container agentic-data-platform-airflow-dag-processor-1  Waiting
 Container agentic-data-platform-clickhouse-1  Waiting
 Container agentic-data-platform-airflow-postgres-1  Waiting
 Container agentic-data-platform-airflow-init-1  Waiting
 Container agentic-data-platform-airflow-api-server-1  Healthy
 Container agentic-data-platform-airflow-init-1  Exited
 Container agentic-data-platform-airflow-dag-processor-1  Healthy
 Container agentic-data-platform-clickhouse-1  Healthy
 Container agentic-data-platform-airflow-postgres-1  Healthy
 Container agentic-data-platform-airflow-scheduler-1  Healthy
```

## make -s airflow-test

Started: 2026-09-05T03:58:46Z
Ended: 2026-09-05T03:59:29Z
Exit code: 0

```text
 Container agentic-data-platform-airflow-postgres-1  Running
 Container agentic-data-platform-airflow-init-1  Created
 Container agentic-data-platform-airflow-dag-processor-1  Running
 Container agentic-data-platform-airflow-api-server-1  Running
 Container agentic-data-platform-airflow-scheduler-1  Running
 Container agentic-data-platform-airflow-postgres-1  Waiting
 Container agentic-data-platform-airflow-postgres-1  Healthy
 Container agentic-data-platform-airflow-init-1  Starting
 Container agentic-data-platform-airflow-init-1  Started
 Container agentic-data-platform-airflow-init-1  Waiting
 Container agentic-data-platform-airflow-postgres-1  Waiting
 Container agentic-data-platform-airflow-init-1  Waiting
 Container agentic-data-platform-airflow-postgres-1  Waiting
 Container agentic-data-platform-airflow-postgres-1  Healthy
 Container agentic-data-platform-airflow-postgres-1  Healthy
 Container agentic-data-platform-airflow-init-1  Exited
 Container agentic-data-platform-airflow-init-1  Waiting
 Container agentic-data-platform-airflow-api-server-1  Waiting
 Container agentic-data-platform-airflow-postgres-1  Waiting
 Container agentic-data-platform-airflow-init-1  Exited
 Container agentic-data-platform-airflow-init-1  Exited
 Container agentic-data-platform-airflow-postgres-1  Healthy
 Container agentic-data-platform-airflow-api-server-1  Healthy
 Container agentic-data-platform-airflow-api-server-1  Waiting
 Container agentic-data-platform-airflow-scheduler-1  Waiting
 Container agentic-data-platform-airflow-dag-processor-1  Waiting
 Container agentic-data-platform-airflow-postgres-1  Waiting
 Container agentic-data-platform-airflow-init-1  Waiting
 Container agentic-data-platform-airflow-init-1  Exited
 Container agentic-data-platform-airflow-scheduler-1  Healthy
 Container agentic-data-platform-airflow-postgres-1  Healthy
 Container agentic-data-platform-airflow-dag-processor-1  Healthy
 Container agentic-data-platform-airflow-api-server-1  Healthy
Airflow API smoke: PASS; dag=ecommerce_hourly; run_id=api_smoke_20260905T035915613875Z_87837881; tasks=6/6 success
```

## make -s airflow-init

Started: 2026-09-05T03:59:29Z
Ended: 2026-09-05T03:59:55Z
Exit code: 0

```text
 Container agentic-data-platform-airflow-postgres-1  Running
 Container agentic-data-platform-airflow-postgres-1  Waiting
 Container agentic-data-platform-airflow-postgres-1  Healthy
2026-09-05T03:59:38.739458Z [info     ] Performing upgrade to the metadata database [airflow.cli.commands.db_command] loc=db_command.py:134 url=postgresql+psycopg2://airflow:***@airflow-postgres:5432/airflow
2026-09-05T03:59:39.236042Z [info     ] Context impl PostgresqlImpl.   [alembic.runtime.migration] loc=migration.py:205
2026-09-05T03:59:39.236271Z [info     ] Will assume transactional DDL. [alembic.runtime.migration] loc=migration.py:208
2026-09-05T03:59:39.243313Z [info     ] Migrating the Airflow database [airflow.utils.db] loc=db.py:1189
2026-09-05T03:59:39.277806Z [info     ] Context impl PostgresqlImpl.   [alembic.runtime.migration] loc=migration.py:205
2026-09-05T03:59:39.277996Z [info     ] Will assume transactional DDL. [alembic.runtime.migration] loc=migration.py:208
2026-09-05T03:59:39.472583Z [info     ] Context impl PostgresqlImpl.   [alembic.runtime.migration] loc=migration.py:205
2026-09-05T03:59:39.472799Z [info     ] Will assume transactional DDL. [alembic.runtime.migration] loc=migration.py:208
2026-09-05T03:59:41.981761Z [warning  ] starlette.middleware.wsgi is deprecated and will be removed in a future release. Please refer to https://github.com/abersheeran/a2wsgi as a replacement. [py.warnings] category=StarletteDeprecationWarning filename=/home/airflow/.local/lib/python3.12/site-packages/fastapi/middleware/wsgi.py lineno=1
2026-09-05T03:59:42.048268Z [info     ] Context impl PostgresqlImpl.   [alembic.runtime.migration] loc=migration.py:205
2026-09-05T03:59:42.048490Z [info     ] Will assume transactional DDL. [alembic.runtime.migration] loc=migration.py:208
2026-09-05T03:59:42.053679Z [info     ] Context impl PostgresqlImpl.   [alembic.runtime.migration] loc=migration.py:205
2026-09-05T03:59:42.053854Z [info     ] Will assume transactional DDL. [alembic.runtime.migration] loc=migration.py:208
2026-09-05T03:59:42.144322Z [info     ] Database migration done!       [airflow.cli.commands.db_command] loc=db_command.py:152
2026-09-05T03:59:50.169185Z [warning  ] starlette.middleware.wsgi is deprecated and will be removed in a future release. Please refer to https://github.com/abersheeran/a2wsgi as a replacement. [py.warnings] category=StarletteDeprecationWarning filename=/home/airflow/.local/lib/python3.12/site-packages/fastapi/middleware/wsgi.py lineno=1
2026-09-05T03:59:50.272036Z [warning  ] Using the in-memory storage for tracking rate limits as no storage was explicitly specified. This is not recommended for production use. See: https://flask-limiter.readthedocs.io#configuring-a-storage-backend for documentation about configuring the storage backend. [py.warnings] category=UserWarning filename=/home/airflow/.local/lib/python3.12/site-packages/flask_limiter/_extension.py lineno=364
airflow already exists in the db
3.3.1
```

## make -s platform-test

Started: 2026-09-05T03:59:55Z
Ended: 2026-09-05T04:00:45Z
Exit code: 0

```text
 Container agentic-data-platform-clickhouse-1  Running
 Container agentic-data-platform-clickhouse-1  Waiting
 Container agentic-data-platform-clickhouse-1  Healthy
Compose can now delegate builds to bake for better performance.
 To do so, set COMPOSE_BAKE=true.
#0 building with "default" instance using docker driver

#1 [dbt internal] load build definition from Dockerfile
#1 transferring dockerfile: 663B done
#1 DONE 0.0s

#2 [dbt internal] load metadata for docker.io/library/python:3.12.14-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254
#2 DONE 0.1s

#3 [dbt internal] load .dockerignore
#3 transferring context: 73B done
#3 DONE 0.0s

#4 [dbt 1/5] FROM docker.io/library/python:3.12.14-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254
#4 DONE 0.0s

#5 [dbt internal] load build context
#5 transferring context: 40B done
#5 DONE 0.0s

#6 [dbt 3/5] COPY requirements.lock /tmp/requirements.lock
#6 CACHED

#7 [dbt 4/5] RUN python -m pip install --requirement /tmp/requirements.lock
#7 CACHED

#8 [dbt 2/5] RUN apt-get update     && apt-get install --yes --no-install-recommends git     && rm -rf /var/lib/apt/lists/*     && groupadd --gid 1000 dbt     && useradd --uid 1000 --gid 1000 --create-home dbt
#8 CACHED

#9 [dbt 5/5] WORKDIR /workspace
#9 CACHED

#10 [dbt] exporting to image
#10 exporting layers done
#10 writing image sha256:299b4b00e44db396a107eb575511d0f20b40c7120d8c9f5bed85f2dbd68a345b 0.0s done
#10 naming to docker.io/library/agentic-data-platform-dbt:1.11.14-1.10.2 0.0s done
#10 DONE 0.0s

#11 [dbt] resolving provenance for metadata file
#11 DONE 0.0s
 dbt  Built
 Container agentic-data-platform-airflow-postgres-1  Running
 Container agentic-data-platform-airflow-init-1  Created
 Container agentic-data-platform-airflow-api-server-1  Running
 Container agentic-data-platform-airflow-dag-processor-1  Running
 Container agentic-data-platform-airflow-scheduler-1  Running
 Container agentic-data-platform-airflow-postgres-1  Waiting
 Container agentic-data-platform-airflow-postgres-1  Healthy
 Container agentic-data-platform-airflow-init-1  Starting
 Container agentic-data-platform-airflow-init-1  Started
 Container agentic-data-platform-airflow-init-1  Waiting
 Container agentic-data-platform-airflow-postgres-1  Waiting
 Container agentic-data-platform-airflow-init-1  Waiting
 Container agentic-data-platform-airflow-postgres-1  Waiting
 Container agentic-data-platform-airflow-postgres-1  Healthy
 Container agentic-data-platform-airflow-postgres-1  Healthy
 Container agentic-data-platform-airflow-init-1  Exited
 Container agentic-data-platform-airflow-init-1  Exited
 Container agentic-data-platform-airflow-api-server-1  Waiting
 Container agentic-data-platform-airflow-postgres-1  Waiting
 Container agentic-data-platform-airflow-init-1  Waiting
 Container agentic-data-platform-airflow-postgres-1  Healthy
 Container agentic-data-platform-airflow-init-1  Exited
 Container agentic-data-platform-airflow-api-server-1  Healthy
 Container agentic-data-platform-airflow-scheduler-1  Waiting
 Container agentic-data-platform-airflow-dag-processor-1  Waiting
 Container agentic-data-platform-airflow-postgres-1  Waiting
 Container agentic-data-platform-airflow-init-1  Waiting
 Container agentic-data-platform-airflow-api-server-1  Waiting
 Container agentic-data-platform-airflow-scheduler-1  Healthy
 Container agentic-data-platform-airflow-api-server-1  Healthy
 Container agentic-data-platform-airflow-postgres-1  Healthy
 Container agentic-data-platform-airflow-dag-processor-1  Healthy
 Container agentic-data-platform-airflow-init-1  Exited
Airflow API smoke: PASS; dag=ecommerce_hourly; run_id=api_smoke_20260905T040025501011Z_4eb212b8; tasks=6/6 success
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
clickhouse baseline: PASS
04:00:39  Running with dbt=1.11.14
04:00:40  Registered adapter: clickhouse=1.10.2
04:00:41  Found 8 models, 68 data tests, 7 sources, 536 macros
04:00:41  
04:00:41  Concurrency: 1 threads (target='dev')
04:00:41  
04:00:41  1 of 68 START test accepted_values_fct_orders_order_status__completed__cancelled__refunded  [RUN]
04:00:41  1 of 68 PASS accepted_values_fct_orders_order_status__completed__cancelled__refunded  [PASS in 0.07s]
04:00:41  2 of 68 START test assert_cancelled_orders_are_unpaid .......................... [RUN]
04:00:41  2 of 68 PASS assert_cancelled_orders_are_unpaid ................................ [PASS in 0.02s]
04:00:41  3 of 68 START test assert_fct_orders_matches_source_count ...................... [RUN]
04:00:41  3 of 68 PASS assert_fct_orders_matches_source_count ............................ [PASS in 0.02s]
04:00:41  4 of 68 START test assert_refunds_do_not_exceed_payments ....................... [RUN]
04:00:41  4 of 68 PASS assert_refunds_do_not_exceed_payments ............................. [PASS in 0.02s]
04:00:41  5 of 68 START test assert_successful_payments_match_orders ..................... [RUN]
04:00:41  5 of 68 PASS assert_successful_payments_match_orders ........................... [PASS in 0.02s]
04:00:41  6 of 68 START test not_null_dim_customers_customer_id .......................... [RUN]
04:00:41  6 of 68 PASS not_null_dim_customers_customer_id ................................ [PASS in 0.02s]
04:00:41  7 of 68 START test not_null_fct_orders_customer_id ............................. [RUN]
04:00:41  7 of 68 PASS not_null_fct_orders_customer_id ................................... [PASS in 0.02s]
04:00:41  8 of 68 START test not_null_fct_orders_order_id ................................ [RUN]
04:00:41  8 of 68 PASS not_null_fct_orders_order_id ...................................... [PASS in 0.02s]
04:00:41  9 of 68 START test not_null_fct_orders_successful_payment_amount_cents ......... [RUN]
04:00:41  9 of 68 PASS not_null_fct_orders_successful_payment_amount_cents ............... [PASS in 0.02s]
04:00:41  10 of 68 START test not_null_fct_orders_successful_refund_amount_cents ......... [RUN]
04:00:41  10 of 68 PASS not_null_fct_orders_successful_refund_amount_cents ............... [PASS in 0.02s]
04:00:41  11 of 68 START test not_null_int_order_payments_order_id ....................... [RUN]
04:00:41  11 of 68 PASS not_null_int_order_payments_order_id ............................. [PASS in 0.02s]
04:00:41  12 of 68 START test not_null_int_order_payments_successful_payment_amount_cents  [RUN]
04:00:41  12 of 68 PASS not_null_int_order_payments_successful_payment_amount_cents ...... [PASS in 0.02s]
04:00:41  13 of 68 START test not_null_int_order_payments_successful_payment_count ....... [RUN]
04:00:41  13 of 68 PASS not_null_int_order_payments_successful_payment_count ............. [PASS in 0.02s]
04:00:41  14 of 68 START test not_null_int_order_refunds_order_id ........................ [RUN]
04:00:41  14 of 68 PASS not_null_int_order_refunds_order_id .............................. [PASS in 0.02s]
04:00:41  15 of 68 START test not_null_int_order_refunds_successful_refund_amount_cents .. [RUN]
04:00:42  15 of 68 PASS not_null_int_order_refunds_successful_refund_amount_cents ........ [PASS in 0.02s]
04:00:42  16 of 68 START test not_null_int_order_refunds_successful_refund_count ......... [RUN]
04:00:42  16 of 68 PASS not_null_int_order_refunds_successful_refund_count ............... [PASS in 0.03s]
04:00:42  17 of 68 START test not_null_stg_customers_customer_id ......................... [RUN]
04:00:42  17 of 68 PASS not_null_stg_customers_customer_id ............................... [PASS in 0.03s]
04:00:42  18 of 68 START test not_null_stg_orders_order_id ............................... [RUN]
04:00:42  18 of 68 PASS not_null_stg_orders_order_id ..................................... [PASS in 0.03s]
04:00:42  19 of 68 START test not_null_stg_payments_payment_id ........................... [RUN]
04:00:42  19 of 68 PASS not_null_stg_payments_payment_id ................................. [PASS in 0.02s]
04:00:42  20 of 68 START test not_null_stg_refunds_refund_id ............................. [RUN]
04:00:42  20 of 68 PASS not_null_stg_refunds_refund_id ................................... [PASS in 0.02s]
04:00:42  21 of 68 START test relationships_fct_orders_customer_id__customer_id__ref_dim_customers_  [RUN]
04:00:42  21 of 68 PASS relationships_fct_orders_customer_id__customer_id__ref_dim_customers_  [PASS in 0.05s]
04:00:42  22 of 68 START test source_accepted_values_raw_customers_country__US__DE__GB__TR__BR  [RUN]
04:00:42  22 of 68 PASS source_accepted_values_raw_customers_country__US__DE__GB__TR__BR . [PASS in 0.03s]
04:00:42  23 of 68 START test source_accepted_values_raw_marketing_attribution_acquisition_channel__organic__paid_search__email__affiliate  [RUN]
04:00:42  23 of 68 PASS source_accepted_values_raw_marketing_attribution_acquisition_channel__organic__paid_search__email__affiliate  [PASS in 0.02s]
04:00:42  24 of 68 START test source_accepted_values_raw_orders_currency__USD__EUR__GBP__TRY  [RUN]
04:00:42  24 of 68 PASS source_accepted_values_raw_orders_currency__USD__EUR__GBP__TRY ... [PASS in 0.02s]
04:00:42  25 of 68 START test source_accepted_values_raw_orders_order_status__completed__cancelled__refunded  [RUN]
04:00:42  25 of 68 PASS source_accepted_values_raw_orders_order_status__completed__cancelled__refunded  [PASS in 0.02s]
04:00:42  26 of 68 START test source_accepted_values_raw_payments_payment_status__succeeded__voided  [RUN]
04:00:42  26 of 68 PASS source_accepted_values_raw_payments_payment_status__succeeded__voided  [PASS in 0.02s]
04:00:42  27 of 68 START test source_accepted_values_raw_refunds_refund_status__succeeded__failed  [RUN]
04:00:42  27 of 68 PASS source_accepted_values_raw_refunds_refund_status__succeeded__failed  [PASS in 0.02s]
04:00:42  28 of 68 START test source_accepted_values_raw_sessions_acquisition_channel__organic__paid_search__email__affiliate  [RUN]
04:00:42  28 of 68 PASS source_accepted_values_raw_sessions_acquisition_channel__organic__paid_search__email__affiliate  [PASS in 0.02s]
04:00:42  29 of 68 START test source_not_null_raw_customers_country ...................... [RUN]
04:00:42  29 of 68 PASS source_not_null_raw_customers_country ............................ [PASS in 0.02s]
04:00:42  30 of 68 START test source_not_null_raw_customers_customer_id .................. [RUN]
04:00:42  30 of 68 PASS source_not_null_raw_customers_customer_id ........................ [PASS in 0.02s]
04:00:42  31 of 68 START test source_not_null_raw_marketing_attribution_attribution_event_id  [RUN]
04:00:42  31 of 68 PASS source_not_null_raw_marketing_attribution_attribution_event_id ... [PASS in 0.02s]
04:00:42  32 of 68 START test source_not_null_raw_marketing_attribution_order_id ......... [RUN]
04:00:42  32 of 68 PASS source_not_null_raw_marketing_attribution_order_id ............... [PASS in 0.02s]
04:00:42  33 of 68 START test source_not_null_raw_marketing_attribution_session_id ....... [RUN]
04:00:42  33 of 68 PASS source_not_null_raw_marketing_attribution_session_id ............. [PASS in 0.02s]
04:00:42  34 of 68 START test source_not_null_raw_order_items_order_id ................... [RUN]
04:00:42  34 of 68 PASS source_not_null_raw_order_items_order_id ......................... [PASS in 0.02s]
04:00:42  35 of 68 START test source_not_null_raw_order_items_order_item_id .............. [RUN]
04:00:42  35 of 68 PASS source_not_null_raw_order_items_order_item_id .................... [PASS in 0.02s]
04:00:42  36 of 68 START test source_not_null_raw_orders_currency ........................ [RUN]
04:00:42  36 of 68 PASS source_not_null_raw_orders_currency .............................. [PASS in 0.02s]
04:00:42  37 of 68 START test source_not_null_raw_orders_customer_id ..................... [RUN]
04:00:42  37 of 68 PASS source_not_null_raw_orders_customer_id ........................... [PASS in 0.02s]
04:00:42  38 of 68 START test source_not_null_raw_orders_order_id ........................ [RUN]
04:00:42  38 of 68 PASS source_not_null_raw_orders_order_id .............................. [PASS in 0.02s]
04:00:42  39 of 68 START test source_not_null_raw_orders_order_status .................... [RUN]
04:00:42  39 of 68 PASS source_not_null_raw_orders_order_status .......................... [PASS in 0.02s]
04:00:42  40 of 68 START test source_not_null_raw_payments_order_id ...................... [RUN]
04:00:42  40 of 68 PASS source_not_null_raw_payments_order_id ............................ [PASS in 0.02s]
04:00:42  41 of 68 START test source_not_null_raw_payments_payment_id .................... [RUN]
04:00:42  41 of 68 PASS source_not_null_raw_payments_payment_id .......................... [PASS in 0.02s]
04:00:42  42 of 68 START test source_not_null_raw_payments_payment_status ................ [RUN]
04:00:42  42 of 68 PASS source_not_null_raw_payments_payment_status ...................... [PASS in 0.02s]
04:00:42  43 of 68 START test source_not_null_raw_refunds_order_id ....................... [RUN]
04:00:42  43 of 68 PASS source_not_null_raw_refunds_order_id ............................. [PASS in 0.02s]
04:00:42  44 of 68 START test source_not_null_raw_refunds_refund_id ...................... [RUN]
04:00:42  44 of 68 PASS source_not_null_raw_refunds_refund_id ............................ [PASS in 0.02s]
04:00:42  45 of 68 START test source_not_null_raw_refunds_refund_status .................. [RUN]
04:00:42  45 of 68 PASS source_not_null_raw_refunds_refund_status ........................ [PASS in 0.02s]
04:00:42  46 of 68 START test source_not_null_raw_sessions_customer_id ................... [RUN]
04:00:42  46 of 68 PASS source_not_null_raw_sessions_customer_id ......................... [PASS in 0.02s]
04:00:42  47 of 68 START test source_not_null_raw_sessions_session_id .................... [RUN]
04:00:42  47 of 68 PASS source_not_null_raw_sessions_session_id .......................... [PASS in 0.02s]
04:00:42  48 of 68 START test source_relationships_raw_marketing_attribution_order_id__order_id__source_raw_orders_  [RUN]
04:00:42  48 of 68 PASS source_relationships_raw_marketing_attribution_order_id__order_id__source_raw_orders_  [PASS in 0.04s]
04:00:42  49 of 68 START test source_relationships_raw_marketing_attribution_session_id__session_id__source_raw_sessions_  [RUN]
04:00:42  49 of 68 PASS source_relationships_raw_marketing_attribution_session_id__session_id__source_raw_sessions_  [PASS in 0.04s]
04:00:42  50 of 68 START test source_relationships_raw_order_items_order_id__order_id__source_raw_orders_  [RUN]
04:00:42  50 of 68 PASS source_relationships_raw_order_items_order_id__order_id__source_raw_orders_  [PASS in 0.03s]
04:00:42  51 of 68 START test source_relationships_raw_orders_customer_id__customer_id__source_raw_customers_  [RUN]
04:00:42  51 of 68 PASS source_relationships_raw_orders_customer_id__customer_id__source_raw_customers_  [PASS in 0.03s]
04:00:42  52 of 68 START test source_relationships_raw_payments_order_id__order_id__source_raw_orders_  [RUN]
04:00:42  52 of 68 PASS source_relationships_raw_payments_order_id__order_id__source_raw_orders_  [PASS in 0.04s]
04:00:42  53 of 68 START test source_relationships_raw_refunds_order_id__order_id__source_raw_orders_  [RUN]
04:00:43  53 of 68 PASS source_relationships_raw_refunds_order_id__order_id__source_raw_orders_  [PASS in 0.03s]
04:00:43  54 of 68 START test source_relationships_raw_sessions_customer_id__customer_id__source_raw_customers_  [RUN]
04:00:43  54 of 68 PASS source_relationships_raw_sessions_customer_id__customer_id__source_raw_customers_  [PASS in 0.03s]
04:00:43  55 of 68 START test source_unique_raw_customers_customer_id .................... [RUN]
04:00:43  55 of 68 PASS source_unique_raw_customers_customer_id .......................... [PASS in 0.02s]
04:00:43  56 of 68 START test source_unique_raw_order_items_order_item_id ................ [RUN]
04:00:43  56 of 68 PASS source_unique_raw_order_items_order_item_id ...................... [PASS in 0.04s]
04:00:43  57 of 68 START test source_unique_raw_orders_order_id .......................... [RUN]
04:00:43  57 of 68 PASS source_unique_raw_orders_order_id ................................ [PASS in 0.05s]
04:00:43  58 of 68 START test source_unique_raw_payments_payment_id ...................... [RUN]
04:00:43  58 of 68 PASS source_unique_raw_payments_payment_id ............................ [PASS in 0.04s]
04:00:43  59 of 68 START test source_unique_raw_refunds_refund_id ........................ [RUN]
04:00:43  59 of 68 PASS source_unique_raw_refunds_refund_id .............................. [PASS in 0.03s]
04:00:43  60 of 68 START test source_unique_raw_sessions_session_id ...................... [RUN]
04:00:43  60 of 68 PASS source_unique_raw_sessions_session_id ............................ [PASS in 0.04s]
04:00:43  61 of 68 START test unique_dim_customers_customer_id ........................... [RUN]
04:00:43  61 of 68 PASS unique_dim_customers_customer_id ................................. [PASS in 0.02s]
04:00:43  62 of 68 START test unique_fct_orders_order_id ................................. [RUN]
04:00:43  62 of 68 PASS unique_fct_orders_order_id ....................................... [PASS in 0.05s]
04:00:43  63 of 68 START test unique_int_order_payments_order_id ......................... [RUN]
04:00:43  63 of 68 PASS unique_int_order_payments_order_id ............................... [PASS in 0.10s]
04:00:43  64 of 68 START test unique_int_order_refunds_order_id .......................... [RUN]
04:00:43  64 of 68 PASS unique_int_order_refunds_order_id ................................ [PASS in 0.02s]
04:00:43  65 of 68 START test unique_stg_customers_customer_id ........................... [RUN]
04:00:43  65 of 68 PASS unique_stg_customers_customer_id ................................. [PASS in 0.02s]
04:00:43  66 of 68 START test unique_stg_orders_order_id ................................. [RUN]
04:00:43  66 of 68 PASS unique_stg_orders_order_id ....................................... [PASS in 0.04s]
04:00:43  67 of 68 START test unique_stg_payments_payment_id ............................. [RUN]
04:00:43  67 of 68 PASS unique_stg_payments_payment_id ................................... [PASS in 0.03s]
04:00:43  68 of 68 START test unique_stg_refunds_refund_id ............................... [RUN]
04:00:43  68 of 68 PASS unique_stg_refunds_refund_id ..................................... [PASS in 0.02s]
04:00:43  
04:00:43  Finished running 68 data tests in 0 hours 0 minutes and 2.48 seconds (2.48s).
04:00:43  
04:00:43  Completed successfully
04:00:43  
04:00:43  Done. PASS=68 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=68
0
0
0
0
0
0
0
0
0
0
0
0
0
dbt baseline: PASS
```

## docker compose --profile tools config --format json | jq -e '[.services | to_entries[] | select(.value.environment.API_TOKEN != null)] | length == 0' && docker compose ps -aq | xargs docker inspect | jq -e '[.[].Config.Env[] | select(startswith("API_TOKEN="))] | length == 0' && docker compose ps --format json | jq -s '[.[] | {Service,State,Health,Publishers}]'

Started: 2026-09-05T04:00:45Z
Ended: 2026-09-05T04:00:45Z
Exit code: 0

```text
true
true
[
  {
    "Service": "airflow-api-server",
    "State": "running",
    "Health": "healthy",
    "Publishers": [
      {
        "URL": "127.0.0.1",
        "TargetPort": 8080,
        "PublishedPort": 8080,
        "Protocol": "tcp"
      }
    ]
  },
  {
    "Service": "airflow-dag-processor",
    "State": "running",
    "Health": "healthy",
    "Publishers": [
      {
        "URL": "",
        "TargetPort": 8080,
        "PublishedPort": 0,
        "Protocol": "tcp"
      }
    ]
  },
  {
    "Service": "airflow-postgres",
    "State": "running",
    "Health": "healthy",
    "Publishers": [
      {
        "URL": "",
        "TargetPort": 5432,
        "PublishedPort": 0,
        "Protocol": "tcp"
      }
    ]
  },
  {
    "Service": "airflow-scheduler",
    "State": "running",
    "Health": "healthy",
    "Publishers": [
      {
        "URL": "",
        "TargetPort": 8080,
        "PublishedPort": 0,
        "Protocol": "tcp"
      }
    ]
  },
  {
    "Service": "clickhouse",
    "State": "running",
    "Health": "healthy",
    "Publishers": [
      {
        "URL": "127.0.0.1",
        "TargetPort": 8123,
        "PublishedPort": 8123,
        "Protocol": "tcp"
      },
      {
        "URL": "127.0.0.1",
        "TargetPort": 9000,
        "PublishedPort": 9000,
        "Protocol": "tcp"
      },
      {
        "URL": "",
        "TargetPort": 9009,
        "PublishedPort": 0,
        "Protocol": "tcp"
      }
    ]
  }
]
```

## date -Iseconds && git rev-parse HEAD && git ls-files --cached --others --exclude-standard platform/airflow docker-compose.yml Makefile .env.example | sort -u | while IFS= read -r path; do if test -f "$path"; then sha256sum "$path"; fi; done | sha256sum

Started: 2026-09-05T04:00:45Z
Ended: 2026-09-05T04:00:45Z
Exit code: 0

```text
2026-09-05T07:00:45+03:00
4e5c70a1f5a46943db8a43405c6bb3ae0b8b8930
13e8a3ab803f5278f98cb0eeb800bbcfc466dc395e5ce02d0162cd62353f3846  -
```
