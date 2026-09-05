# Fresh dbt baseline gate

Source includes uncommitted changes; scoped tree hash is SHA256 of sorted path/checksum lines for platform/dbt and platform/clickhouse.

## date -Iseconds && git rev-parse HEAD && git status --porcelain=v1 | wc -l && docker image inspect agentic-data-platform-dbt:1.11.14-1.10.2 --format '{{.Id}}' && git ls-files --cached --others --exclude-standard platform/dbt platform/clickhouse | sort -u | while IFS= read -r path; do if test -f "$path"; then sha256sum "$path"; fi; done | sha256sum

Started: 2026-09-05T03:50:10Z
Ended: 2026-09-05T03:50:10Z
Exit code: 0

```text
2026-09-05T06:50:10+03:00
4e5c70a1f5a46943db8a43405c6bb3ae0b8b8930
20
sha256:299b4b00e44db396a107eb575511d0f20b40c7120d8c9f5bed85f2dbd68a345b
a6ca3950b13d7b1c5e025f4374d01ab9c0054745a0b7ef051a1aaffbd42b4972  -
```

## make -s dbt-version dbt-debug dbt-parse dbt-compile

Started: 2026-09-05T03:50:10Z
Ended: 2026-09-05T03:51:27Z
Exit code: 0

```text
Compose can now delegate builds to bake for better performance.
 To do so, set COMPOSE_BAKE=true.
#0 building with "default" instance using docker driver

#1 [dbt internal] load build definition from Dockerfile
#1 transferring dockerfile: 663B done
#1 DONE 0.0s

#2 [dbt internal] load metadata for docker.io/library/python:3.12.14-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254
#2 DONE 1.1s

#3 [dbt internal] load .dockerignore
#3 transferring context: 73B done
#3 DONE 0.0s

#4 [dbt 1/5] FROM docker.io/library/python:3.12.14-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254
#4 DONE 0.0s

#5 [dbt internal] load build context
#5 transferring context: 40B done
#5 DONE 0.0s

#6 [dbt 4/5] RUN python -m pip install --requirement /tmp/requirements.lock
#6 CACHED

#7 [dbt 2/5] RUN apt-get update     && apt-get install --yes --no-install-recommends git     && rm -rf /var/lib/apt/lists/*     && groupadd --gid 1000 dbt     && useradd --uid 1000 --gid 1000 --create-home dbt
#7 CACHED

#8 [dbt 3/5] COPY requirements.lock /tmp/requirements.lock
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
Core:
  - installed: 1.11.14
  - latest:    1.12.3  - Update available!

  Your version of dbt-core is out of date!
  You can find instructions for upgrading here:
  https://docs.getdbt.com/docs/installation

Plugins:
  - clickhouse: 1.10.2 - Up to date!


 Container agentic-data-platform-clickhouse-1  Running
 Container agentic-data-platform-clickhouse-1  Waiting
 Container agentic-data-platform-clickhouse-1  Healthy
03:50:29  Running with dbt=1.11.14
03:50:29  dbt version: 1.11.14
03:50:29  python version: 3.12.14
03:50:29  python path: /usr/local/bin/python
03:50:29  os info: Linux-7.0.0-30-generic-x86_64-with-glibc2.36
03:50:29  Using profiles dir at /workspace
03:50:29  Using profiles.yml file at /workspace/profiles.yml
03:50:29  Using dbt_project.yml file at /workspace/dbt_project.yml
03:50:29  adapter type: clickhouse
03:50:29  adapter version: 1.10.2
03:50:29  Configuration:
03:50:29    profiles.yml file [OK found and valid]
03:50:29    dbt_project.yml file [OK found and valid]
03:50:29  Required dependencies:
03:50:30   - git [OK found]

03:50:30  Connection:
03:50:30    driver: http
03:50:30    host: clickhouse
03:50:30    port: 8123
03:50:30    user: agentic
03:50:30    schema: analytics
03:50:30    retries: 2
03:50:30    cluster: None
03:50:30    database_engine: None
03:50:30    cluster_mode: False
03:50:30    secure: False
03:50:30    verify: False
03:50:30    client_cert: None
03:50:30    client_cert_key: None
03:50:30    connect_timeout: 10
03:50:30    send_receive_timeout: 300
03:50:30    sync_request_timeout: 5
03:50:30    compress_block_size: 1048576
03:50:30    compression: 
03:50:30    check_exchange: True
03:50:30    custom_settings: {'join_use_nulls': 1}
03:50:30    use_lw_deletes: False
03:50:30    allow_automatic_deduplication: False
03:50:30    tcp_keepalive: False
03:50:30    reuse_connections: True
03:50:30    server_host_name: None
03:50:30  Registered adapter: clickhouse=1.10.2
03:50:30    Connection test: [OK connection ok]

03:50:30  All checks passed!
03:50:35  Running with dbt=1.11.14
03:50:35  Registered adapter: clickhouse=1.10.2
03:50:38  Performance info: /workspace/target/perf_info.json
03:51:24  Running with dbt=1.11.14
03:51:24  Registered adapter: clickhouse=1.10.2
03:51:25  Found 8 models, 68 data tests, 7 sources, 536 macros
03:51:25  
03:51:25  Concurrency: 1 threads (target='dev')
03:51:25
```

## make -s dbt-build dbt-test clickhouse-test dbt-baseline-test

Started: 2026-09-05T03:51:27Z
Ended: 2026-09-05T03:51:48Z
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
#1 DONE 0.4s

#2 [dbt internal] load metadata for docker.io/library/python:3.12.14-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254
#2 DONE 0.1s

#3 [dbt internal] load .dockerignore
#3 transferring context:
#3 transferring context: 73B done
#3 DONE 0.0s

#4 [dbt 1/5] FROM docker.io/library/python:3.12.14-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254
#4 DONE 0.0s

#5 [dbt internal] load build context
#5 transferring context: 40B done
#5 DONE 0.4s

#6 [dbt 2/5] RUN apt-get update     && apt-get install --yes --no-install-recommends git     && rm -rf /var/lib/apt/lists/*     && groupadd --gid 1000 dbt     && useradd --uid 1000 --gid 1000 --create-home dbt
#6 CACHED

#7 [dbt 3/5] COPY requirements.lock /tmp/requirements.lock
#7 CACHED

#8 [dbt 4/5] RUN python -m pip install --requirement /tmp/requirements.lock
#8 CACHED

#9 [dbt 5/5] WORKDIR /workspace
#9 CACHED

#10 [dbt] exporting to image
#10 exporting layers done
#10 writing image sha256:299b4b00e44db396a107eb575511d0f20b40c7120d8c9f5bed85f2dbd68a345b
#10 writing image sha256:299b4b00e44db396a107eb575511d0f20b40c7120d8c9f5bed85f2dbd68a345b 0.3s done
#10 naming to docker.io/library/agentic-data-platform-dbt:1.11.14-1.10.2
#10 naming to docker.io/library/agentic-data-platform-dbt:1.11.14-1.10.2 0.0s done
#10 DONE 0.4s

#11 [dbt] resolving provenance for metadata file
 dbt  Built
#11 DONE 0.0s
03:51:33  Running with dbt=1.11.14
03:51:34  Registered adapter: clickhouse=1.10.2
03:51:34  Found 8 models, 68 data tests, 7 sources, 536 macros
03:51:34  
03:51:34  Concurrency: 1 threads (target='dev')
03:51:34  
03:51:35  1 of 76 START test source_accepted_values_raw_customers_country__US__DE__GB__TR__BR  [RUN]
03:51:35  1 of 76 PASS source_accepted_values_raw_customers_country__US__DE__GB__TR__BR .. [PASS in 0.07s]
03:51:35  2 of 76 START test source_accepted_values_raw_marketing_attribution_acquisition_channel__organic__paid_search__email__affiliate  [RUN]
03:51:35  2 of 76 PASS source_accepted_values_raw_marketing_attribution_acquisition_channel__organic__paid_search__email__affiliate  [PASS in 0.03s]
03:51:35  3 of 76 START test source_accepted_values_raw_orders_currency__USD__EUR__GBP__TRY  [RUN]
03:51:35  3 of 76 PASS source_accepted_values_raw_orders_currency__USD__EUR__GBP__TRY .... [PASS in 0.03s]
03:51:35  4 of 76 START test source_accepted_values_raw_orders_order_status__completed__cancelled__refunded  [RUN]
03:51:35  4 of 76 PASS source_accepted_values_raw_orders_order_status__completed__cancelled__refunded  [PASS in 0.03s]
03:51:35  5 of 76 START test source_accepted_values_raw_payments_payment_status__succeeded__voided  [RUN]
03:51:35  5 of 76 PASS source_accepted_values_raw_payments_payment_status__succeeded__voided  [PASS in 0.02s]
03:51:35  6 of 76 START test source_accepted_values_raw_refunds_refund_status__succeeded__failed  [RUN]
03:51:35  6 of 76 PASS source_accepted_values_raw_refunds_refund_status__succeeded__failed  [PASS in 0.02s]
03:51:35  7 of 76 START test source_accepted_values_raw_sessions_acquisition_channel__organic__paid_search__email__affiliate  [RUN]
03:51:35  7 of 76 PASS source_accepted_values_raw_sessions_acquisition_channel__organic__paid_search__email__affiliate  [PASS in 0.02s]
03:51:35  8 of 76 START test source_not_null_raw_customers_country ....................... [RUN]
03:51:35  8 of 76 PASS source_not_null_raw_customers_country ............................. [PASS in 0.03s]
03:51:35  9 of 76 START test source_not_null_raw_customers_customer_id ................... [RUN]
03:51:35  9 of 76 PASS source_not_null_raw_customers_customer_id ......................... [PASS in 0.02s]
03:51:35  10 of 76 START test source_not_null_raw_marketing_attribution_attribution_event_id  [RUN]
03:51:35  10 of 76 PASS source_not_null_raw_marketing_attribution_attribution_event_id ... [PASS in 0.02s]
03:51:35  11 of 76 START test source_not_null_raw_marketing_attribution_order_id ......... [RUN]
03:51:35  11 of 76 PASS source_not_null_raw_marketing_attribution_order_id ............... [PASS in 0.02s]
03:51:35  12 of 76 START test source_not_null_raw_marketing_attribution_session_id ....... [RUN]
03:51:35  12 of 76 PASS source_not_null_raw_marketing_attribution_session_id ............. [PASS in 0.02s]
03:51:35  13 of 76 START test source_not_null_raw_order_items_order_id ................... [RUN]
03:51:35  13 of 76 PASS source_not_null_raw_order_items_order_id ......................... [PASS in 0.02s]
03:51:35  14 of 76 START test source_not_null_raw_order_items_order_item_id .............. [RUN]
03:51:35  14 of 76 PASS source_not_null_raw_order_items_order_item_id .................... [PASS in 0.02s]
03:51:35  15 of 76 START test source_not_null_raw_orders_currency ........................ [RUN]
03:51:35  15 of 76 PASS source_not_null_raw_orders_currency .............................. [PASS in 0.02s]
03:51:35  16 of 76 START test source_not_null_raw_orders_customer_id ..................... [RUN]
03:51:35  16 of 76 PASS source_not_null_raw_orders_customer_id ........................... [PASS in 0.02s]
03:51:35  17 of 76 START test source_not_null_raw_orders_order_id ........................ [RUN]
03:51:35  17 of 76 PASS source_not_null_raw_orders_order_id .............................. [PASS in 0.02s]
03:51:35  18 of 76 START test source_not_null_raw_orders_order_status .................... [RUN]
03:51:35  18 of 76 PASS source_not_null_raw_orders_order_status .......................... [PASS in 0.02s]
03:51:35  19 of 76 START test source_not_null_raw_payments_order_id ...................... [RUN]
03:51:35  19 of 76 PASS source_not_null_raw_payments_order_id ............................ [PASS in 0.02s]
03:51:35  20 of 76 START test source_not_null_raw_payments_payment_id .................... [RUN]
03:51:35  20 of 76 PASS source_not_null_raw_payments_payment_id .......................... [PASS in 0.02s]
03:51:35  21 of 76 START test source_not_null_raw_payments_payment_status ................ [RUN]
03:51:35  21 of 76 PASS source_not_null_raw_payments_payment_status ...................... [PASS in 0.02s]
03:51:35  22 of 76 START test source_not_null_raw_refunds_order_id ....................... [RUN]
03:51:35  22 of 76 PASS source_not_null_raw_refunds_order_id ............................. [PASS in 0.02s]
03:51:35  23 of 76 START test source_not_null_raw_refunds_refund_id ...................... [RUN]
03:51:35  23 of 76 PASS source_not_null_raw_refunds_refund_id ............................ [PASS in 0.02s]
03:51:35  24 of 76 START test source_not_null_raw_refunds_refund_status .................. [RUN]
03:51:35  24 of 76 PASS source_not_null_raw_refunds_refund_status ........................ [PASS in 0.02s]
03:51:35  25 of 76 START test source_not_null_raw_sessions_customer_id ................... [RUN]
03:51:35  25 of 76 PASS source_not_null_raw_sessions_customer_id ......................... [PASS in 0.02s]
03:51:35  26 of 76 START test source_not_null_raw_sessions_session_id .................... [RUN]
03:51:35  26 of 76 PASS source_not_null_raw_sessions_session_id .......................... [PASS in 0.02s]
03:51:35  27 of 76 START test source_relationships_raw_marketing_attribution_order_id__order_id__source_raw_orders_  [RUN]
03:51:36  27 of 76 PASS source_relationships_raw_marketing_attribution_order_id__order_id__source_raw_orders_  [PASS in 0.07s]
03:51:36  28 of 76 START test source_relationships_raw_marketing_attribution_session_id__session_id__source_raw_sessions_  [RUN]
03:51:36  28 of 76 PASS source_relationships_raw_marketing_attribution_session_id__session_id__source_raw_sessions_  [PASS in 0.06s]
03:51:36  29 of 76 START test source_relationships_raw_order_items_order_id__order_id__source_raw_orders_  [RUN]
03:51:36  29 of 76 PASS source_relationships_raw_order_items_order_id__order_id__source_raw_orders_  [PASS in 0.05s]
03:51:36  30 of 76 START test source_relationships_raw_orders_customer_id__customer_id__source_raw_customers_  [RUN]
03:51:36  30 of 76 PASS source_relationships_raw_orders_customer_id__customer_id__source_raw_customers_  [PASS in 0.04s]
03:51:36  31 of 76 START test source_relationships_raw_payments_order_id__order_id__source_raw_orders_  [RUN]
03:51:36  31 of 76 PASS source_relationships_raw_payments_order_id__order_id__source_raw_orders_  [PASS in 0.04s]
03:51:36  32 of 76 START test source_relationships_raw_refunds_order_id__order_id__source_raw_orders_  [RUN]
03:51:36  32 of 76 PASS source_relationships_raw_refunds_order_id__order_id__source_raw_orders_  [PASS in 0.04s]
03:51:36  33 of 76 START test source_relationships_raw_sessions_customer_id__customer_id__source_raw_customers_  [RUN]
03:51:36  33 of 76 PASS source_relationships_raw_sessions_customer_id__customer_id__source_raw_customers_  [PASS in 0.05s]
03:51:36  34 of 76 START test source_unique_raw_customers_customer_id .................... [RUN]
03:51:36  34 of 76 PASS source_unique_raw_customers_customer_id .......................... [PASS in 0.04s]
03:51:36  35 of 76 START test source_unique_raw_order_items_order_item_id ................ [RUN]
03:51:36  35 of 76 PASS source_unique_raw_order_items_order_item_id ...................... [PASS in 0.36s]
03:51:36  36 of 76 START test source_unique_raw_orders_order_id .......................... [RUN]
03:51:36  36 of 76 PASS source_unique_raw_orders_order_id ................................ [PASS in 0.04s]
03:51:36  37 of 76 START test source_unique_raw_payments_payment_id ...................... [RUN]
03:51:36  37 of 76 PASS source_unique_raw_payments_payment_id ............................ [PASS in 0.04s]
03:51:36  38 of 76 START test source_unique_raw_refunds_refund_id ........................ [RUN]
03:51:36  38 of 76 PASS source_unique_raw_refunds_refund_id .............................. [PASS in 0.02s]
03:51:36  39 of 76 START test source_unique_raw_sessions_session_id ...................... [RUN]
03:51:36  39 of 76 PASS source_unique_raw_sessions_session_id ............................ [PASS in 0.03s]
03:51:36  40 of 76 START sql view model `analytics`.`stg_customers` ...................... [RUN]
03:51:36  40 of 76 OK created sql view model `analytics`.`stg_customers` ................. [OK in 0.13s]
03:51:36  41 of 76 START sql view model `analytics`.`stg_orders` ......................... [RUN]
03:51:37  41 of 76 OK created sql view model `analytics`.`stg_orders` .................... [OK in 0.29s]
03:51:37  42 of 76 START sql view model `analytics`.`stg_payments` ....................... [RUN]
03:51:37  42 of 76 OK created sql view model `analytics`.`stg_payments` .................. [OK in 0.06s]
03:51:37  43 of 76 START sql view model `analytics`.`stg_refunds` ........................ [RUN]
03:51:37  43 of 76 OK created sql view model `analytics`.`stg_refunds` ................... [OK in 0.09s]
03:51:37  44 of 76 START test not_null_stg_customers_customer_id ......................... [RUN]
03:51:37  44 of 76 PASS not_null_stg_customers_customer_id ............................... [PASS in 0.02s]
03:51:37  45 of 76 START test unique_stg_customers_customer_id ........................... [RUN]
03:51:37  45 of 76 PASS unique_stg_customers_customer_id ................................. [PASS in 0.02s]
03:51:37  46 of 76 START test not_null_stg_orders_order_id ............................... [RUN]
03:51:37  46 of 76 PASS not_null_stg_orders_order_id ..................................... [PASS in 0.02s]
03:51:37  47 of 76 START test unique_stg_orders_order_id ................................. [RUN]
03:51:37  47 of 76 PASS unique_stg_orders_order_id ....................................... [PASS in 0.03s]
03:51:37  48 of 76 START test not_null_stg_payments_payment_id ........................... [RUN]
03:51:37  48 of 76 PASS not_null_stg_payments_payment_id ................................. [PASS in 0.02s]
03:51:37  49 of 76 START test unique_stg_payments_payment_id ............................. [RUN]
03:51:37  49 of 76 PASS unique_stg_payments_payment_id ................................... [PASS in 0.03s]
03:51:37  50 of 76 START test not_null_stg_refunds_refund_id ............................. [RUN]
03:51:37  50 of 76 PASS not_null_stg_refunds_refund_id ................................... [PASS in 0.02s]
03:51:37  51 of 76 START test unique_stg_refunds_refund_id ............................... [RUN]
03:51:37  51 of 76 PASS unique_stg_refunds_refund_id ..................................... [PASS in 0.02s]
03:51:37  52 of 76 START sql table model `analytics`.`dim_customers` ..................... [RUN]
03:51:38  52 of 76 OK created sql table model `analytics`.`dim_customers` ................ [OK in 0.49s]
03:51:38  53 of 76 START sql view model `analytics`.`int_order_payments` ................. [RUN]
03:51:38  53 of 76 OK created sql view model `analytics`.`int_order_payments` ............ [OK in 0.05s]
03:51:38  54 of 76 START sql view model `analytics`.`int_order_refunds` .................. [RUN]
03:51:38  54 of 76 OK created sql view model `analytics`.`int_order_refunds` ............. [OK in 0.04s]
03:51:38  55 of 76 START test not_null_dim_customers_customer_id ......................... [RUN]
03:51:38  55 of 76 PASS not_null_dim_customers_customer_id ............................... [PASS in 0.02s]
03:51:38  56 of 76 START test unique_dim_customers_customer_id ........................... [RUN]
03:51:38  56 of 76 PASS unique_dim_customers_customer_id ................................. [PASS in 0.02s]
03:51:38  57 of 76 START test not_null_int_order_payments_order_id ....................... [RUN]
03:51:38  57 of 76 PASS not_null_int_order_payments_order_id ............................. [PASS in 0.02s]
03:51:38  58 of 76 START test not_null_int_order_payments_successful_payment_amount_cents  [RUN]
03:51:38  58 of 76 PASS not_null_int_order_payments_successful_payment_amount_cents ...... [PASS in 0.05s]
03:51:38  59 of 76 START test not_null_int_order_payments_successful_payment_count ....... [RUN]
03:51:38  59 of 76 PASS not_null_int_order_payments_successful_payment_count ............. [PASS in 0.02s]
03:51:38  60 of 76 START test unique_int_order_payments_order_id ......................... [RUN]
03:51:38  60 of 76 PASS unique_int_order_payments_order_id ............................... [PASS in 0.04s]
03:51:38  61 of 76 START test not_null_int_order_refunds_order_id ........................ [RUN]
03:51:38  61 of 76 PASS not_null_int_order_refunds_order_id .............................. [PASS in 0.02s]
03:51:38  62 of 76 START test not_null_int_order_refunds_successful_refund_amount_cents .. [RUN]
03:51:38  62 of 76 PASS not_null_int_order_refunds_successful_refund_amount_cents ........ [PASS in 0.02s]
03:51:38  63 of 76 START test not_null_int_order_refunds_successful_refund_count ......... [RUN]
03:51:38  63 of 76 PASS not_null_int_order_refunds_successful_refund_count ............... [PASS in 0.02s]
03:51:38  64 of 76 START test unique_int_order_refunds_order_id .......................... [RUN]
03:51:38  64 of 76 PASS unique_int_order_refunds_order_id ................................ [PASS in 0.02s]
03:51:38  65 of 76 START sql table model `analytics`.`fct_orders` ........................ [RUN]
03:51:38  65 of 76 OK created sql table model `analytics`.`fct_orders` ................... [OK in 0.19s]
03:51:38  66 of 76 START test accepted_values_fct_orders_order_status__completed__cancelled__refunded  [RUN]
03:51:38  66 of 76 PASS accepted_values_fct_orders_order_status__completed__cancelled__refunded  [PASS in 0.02s]
03:51:38  67 of 76 START test assert_cancelled_orders_are_unpaid ......................... [RUN]
03:51:38  67 of 76 PASS assert_cancelled_orders_are_unpaid ............................... [PASS in 0.02s]
03:51:38  68 of 76 START test assert_fct_orders_matches_source_count ..................... [RUN]
03:51:38  68 of 76 PASS assert_fct_orders_matches_source_count ........................... [PASS in 0.02s]
03:51:38  69 of 76 START test assert_refunds_do_not_exceed_payments ...................... [RUN]
03:51:38  69 of 76 PASS assert_refunds_do_not_exceed_payments ............................ [PASS in 0.02s]
03:51:38  70 of 76 START test assert_successful_payments_match_orders .................... [RUN]
03:51:38  70 of 76 PASS assert_successful_payments_match_orders .......................... [PASS in 0.02s]
03:51:38  71 of 76 START test not_null_fct_orders_customer_id ............................ [RUN]
03:51:38  71 of 76 PASS not_null_fct_orders_customer_id .................................. [PASS in 0.02s]
03:51:38  72 of 76 START test not_null_fct_orders_order_id ............................... [RUN]
03:51:38  72 of 76 PASS not_null_fct_orders_order_id ..................................... [PASS in 0.02s]
03:51:38  73 of 76 START test not_null_fct_orders_successful_payment_amount_cents ........ [RUN]
03:51:38  73 of 76 PASS not_null_fct_orders_successful_payment_amount_cents .............. [PASS in 0.02s]
03:51:38  74 of 76 START test not_null_fct_orders_successful_refund_amount_cents ......... [RUN]
03:51:38  74 of 76 PASS not_null_fct_orders_successful_refund_amount_cents ............... [PASS in 0.02s]
03:51:38  75 of 76 START test relationships_fct_orders_customer_id__customer_id__ref_dim_customers_  [RUN]
03:51:38  75 of 76 PASS relationships_fct_orders_customer_id__customer_id__ref_dim_customers_  [PASS in 0.03s]
03:51:38  76 of 76 START test unique_fct_orders_order_id ................................. [RUN]
03:51:39  76 of 76 PASS unique_fct_orders_order_id ....................................... [PASS in 0.04s]
03:51:39  
03:51:39  Finished running 2 table models, 68 data tests, 6 view models in 0 hours 0 minutes and 4.17 seconds (4.17s).
03:51:39  
03:51:39  Completed successfully
03:51:39  
03:51:39  Done. PASS=76 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=76
03:51:43  Running with dbt=1.11.14
03:51:43  Registered adapter: clickhouse=1.10.2
03:51:44  Found 8 models, 68 data tests, 7 sources, 536 macros
03:51:44  
03:51:44  Concurrency: 1 threads (target='dev')
03:51:44  
03:51:45  1 of 68 START test accepted_values_fct_orders_order_status__completed__cancelled__refunded  [RUN]
03:51:45  1 of 68 PASS accepted_values_fct_orders_order_status__completed__cancelled__refunded  [PASS in 0.07s]
03:51:45  2 of 68 START test assert_cancelled_orders_are_unpaid .......................... [RUN]
03:51:45  2 of 68 PASS assert_cancelled_orders_are_unpaid ................................ [PASS in 0.02s]
03:51:45  3 of 68 START test assert_fct_orders_matches_source_count ...................... [RUN]
03:51:45  3 of 68 PASS assert_fct_orders_matches_source_count ............................ [PASS in 0.02s]
03:51:45  4 of 68 START test assert_refunds_do_not_exceed_payments ....................... [RUN]
03:51:45  4 of 68 PASS assert_refunds_do_not_exceed_payments ............................. [PASS in 0.02s]
03:51:45  5 of 68 START test assert_successful_payments_match_orders ..................... [RUN]
03:51:45  5 of 68 PASS assert_successful_payments_match_orders ........................... [PASS in 0.02s]
03:51:45  6 of 68 START test not_null_dim_customers_customer_id .......................... [RUN]
03:51:45  6 of 68 PASS not_null_dim_customers_customer_id ................................ [PASS in 0.03s]
03:51:45  7 of 68 START test not_null_fct_orders_customer_id ............................. [RUN]
03:51:45  7 of 68 PASS not_null_fct_orders_customer_id ................................... [PASS in 0.02s]
03:51:45  8 of 68 START test not_null_fct_orders_order_id ................................ [RUN]
03:51:45  8 of 68 PASS not_null_fct_orders_order_id ...................................... [PASS in 0.02s]
03:51:45  9 of 68 START test not_null_fct_orders_successful_payment_amount_cents ......... [RUN]
03:51:45  9 of 68 PASS not_null_fct_orders_successful_payment_amount_cents ............... [PASS in 0.02s]
03:51:45  10 of 68 START test not_null_fct_orders_successful_refund_amount_cents ......... [RUN]
03:51:45  10 of 68 PASS not_null_fct_orders_successful_refund_amount_cents ............... [PASS in 0.02s]
03:51:45  11 of 68 START test not_null_int_order_payments_order_id ....................... [RUN]
03:51:45  11 of 68 PASS not_null_int_order_payments_order_id ............................. [PASS in 0.02s]
03:51:45  12 of 68 START test not_null_int_order_payments_successful_payment_amount_cents  [RUN]
03:51:45  12 of 68 PASS not_null_int_order_payments_successful_payment_amount_cents ...... [PASS in 0.02s]
03:51:45  13 of 68 START test not_null_int_order_payments_successful_payment_count ....... [RUN]
03:51:45  13 of 68 PASS not_null_int_order_payments_successful_payment_count ............. [PASS in 0.02s]
03:51:45  14 of 68 START test not_null_int_order_refunds_order_id ........................ [RUN]
03:51:45  14 of 68 PASS not_null_int_order_refunds_order_id .............................. [PASS in 0.02s]
03:51:45  15 of 68 START test not_null_int_order_refunds_successful_refund_amount_cents .. [RUN]
03:51:45  15 of 68 PASS not_null_int_order_refunds_successful_refund_amount_cents ........ [PASS in 0.02s]
03:51:45  16 of 68 START test not_null_int_order_refunds_successful_refund_count ......... [RUN]
03:51:45  16 of 68 PASS not_null_int_order_refunds_successful_refund_count ............... [PASS in 0.02s]
03:51:45  17 of 68 START test not_null_stg_customers_customer_id ......................... [RUN]
03:51:45  17 of 68 PASS not_null_stg_customers_customer_id ............................... [PASS in 0.02s]
03:51:45  18 of 68 START test not_null_stg_orders_order_id ............................... [RUN]
03:51:45  18 of 68 PASS not_null_stg_orders_order_id ..................................... [PASS in 0.02s]
03:51:45  19 of 68 START test not_null_stg_payments_payment_id ........................... [RUN]
03:51:45  19 of 68 PASS not_null_stg_payments_payment_id ................................. [PASS in 0.02s]
03:51:45  20 of 68 START test not_null_stg_refunds_refund_id ............................. [RUN]
03:51:45  20 of 68 PASS not_null_stg_refunds_refund_id ................................... [PASS in 0.02s]
03:51:45  21 of 68 START test relationships_fct_orders_customer_id__customer_id__ref_dim_customers_  [RUN]
03:51:45  21 of 68 PASS relationships_fct_orders_customer_id__customer_id__ref_dim_customers_  [PASS in 0.03s]
03:51:45  22 of 68 START test source_accepted_values_raw_customers_country__US__DE__GB__TR__BR  [RUN]
03:51:45  22 of 68 PASS source_accepted_values_raw_customers_country__US__DE__GB__TR__BR . [PASS in 0.03s]
03:51:45  23 of 68 START test source_accepted_values_raw_marketing_attribution_acquisition_channel__organic__paid_search__email__affiliate  [RUN]
03:51:45  23 of 68 PASS source_accepted_values_raw_marketing_attribution_acquisition_channel__organic__paid_search__email__affiliate  [PASS in 0.02s]
03:51:45  24 of 68 START test source_accepted_values_raw_orders_currency__USD__EUR__GBP__TRY  [RUN]
03:51:45  24 of 68 PASS source_accepted_values_raw_orders_currency__USD__EUR__GBP__TRY ... [PASS in 0.02s]
03:51:45  25 of 68 START test source_accepted_values_raw_orders_order_status__completed__cancelled__refunded  [RUN]
03:51:45  25 of 68 PASS source_accepted_values_raw_orders_order_status__completed__cancelled__refunded  [PASS in 0.02s]
03:51:45  26 of 68 START test source_accepted_values_raw_payments_payment_status__succeeded__voided  [RUN]
03:51:45  26 of 68 PASS source_accepted_values_raw_payments_payment_status__succeeded__voided  [PASS in 0.02s]
03:51:45  27 of 68 START test source_accepted_values_raw_refunds_refund_status__succeeded__failed  [RUN]
03:51:45  27 of 68 PASS source_accepted_values_raw_refunds_refund_status__succeeded__failed  [PASS in 0.02s]
03:51:45  28 of 68 START test source_accepted_values_raw_sessions_acquisition_channel__organic__paid_search__email__affiliate  [RUN]
03:51:45  28 of 68 PASS source_accepted_values_raw_sessions_acquisition_channel__organic__paid_search__email__affiliate  [PASS in 0.02s]
03:51:45  29 of 68 START test source_not_null_raw_customers_country ...................... [RUN]
03:51:45  29 of 68 PASS source_not_null_raw_customers_country ............................ [PASS in 0.02s]
03:51:45  30 of 68 START test source_not_null_raw_customers_customer_id .................. [RUN]
03:51:45  30 of 68 PASS source_not_null_raw_customers_customer_id ........................ [PASS in 0.02s]
03:51:45  31 of 68 START test source_not_null_raw_marketing_attribution_attribution_event_id  [RUN]
03:51:45  31 of 68 PASS source_not_null_raw_marketing_attribution_attribution_event_id ... [PASS in 0.02s]
03:51:45  32 of 68 START test source_not_null_raw_marketing_attribution_order_id ......... [RUN]
03:51:45  32 of 68 PASS source_not_null_raw_marketing_attribution_order_id ............... [PASS in 0.02s]
03:51:45  33 of 68 START test source_not_null_raw_marketing_attribution_session_id ....... [RUN]
03:51:45  33 of 68 PASS source_not_null_raw_marketing_attribution_session_id ............. [PASS in 0.02s]
03:51:45  34 of 68 START test source_not_null_raw_order_items_order_id ................... [RUN]
03:51:45  34 of 68 PASS source_not_null_raw_order_items_order_id ......................... [PASS in 0.02s]
03:51:45  35 of 68 START test source_not_null_raw_order_items_order_item_id .............. [RUN]
03:51:45  35 of 68 PASS source_not_null_raw_order_items_order_item_id .................... [PASS in 0.02s]
03:51:45  36 of 68 START test source_not_null_raw_orders_currency ........................ [RUN]
03:51:45  36 of 68 PASS source_not_null_raw_orders_currency .............................. [PASS in 0.02s]
03:51:45  37 of 68 START test source_not_null_raw_orders_customer_id ..................... [RUN]
03:51:45  37 of 68 PASS source_not_null_raw_orders_customer_id ........................... [PASS in 0.02s]
03:51:45  38 of 68 START test source_not_null_raw_orders_order_id ........................ [RUN]
03:51:45  38 of 68 PASS source_not_null_raw_orders_order_id .............................. [PASS in 0.02s]
03:51:45  39 of 68 START test source_not_null_raw_orders_order_status .................... [RUN]
03:51:46  39 of 68 PASS source_not_null_raw_orders_order_status .......................... [PASS in 0.02s]
03:51:46  40 of 68 START test source_not_null_raw_payments_order_id ...................... [RUN]
03:51:46  40 of 68 PASS source_not_null_raw_payments_order_id ............................ [PASS in 0.02s]
03:51:46  41 of 68 START test source_not_null_raw_payments_payment_id .................... [RUN]
03:51:46  41 of 68 PASS source_not_null_raw_payments_payment_id .......................... [PASS in 0.02s]
03:51:46  42 of 68 START test source_not_null_raw_payments_payment_status ................ [RUN]
03:51:46  42 of 68 PASS source_not_null_raw_payments_payment_status ...................... [PASS in 0.02s]
03:51:46  43 of 68 START test source_not_null_raw_refunds_order_id ....................... [RUN]
03:51:46  43 of 68 PASS source_not_null_raw_refunds_order_id ............................. [PASS in 0.02s]
03:51:46  44 of 68 START test source_not_null_raw_refunds_refund_id ...................... [RUN]
03:51:46  44 of 68 PASS source_not_null_raw_refunds_refund_id ............................ [PASS in 0.02s]
03:51:46  45 of 68 START test source_not_null_raw_refunds_refund_status .................. [RUN]
03:51:46  45 of 68 PASS source_not_null_raw_refunds_refund_status ........................ [PASS in 0.02s]
03:51:46  46 of 68 START test source_not_null_raw_sessions_customer_id ................... [RUN]
03:51:46  46 of 68 PASS source_not_null_raw_sessions_customer_id ......................... [PASS in 0.02s]
03:51:46  47 of 68 START test source_not_null_raw_sessions_session_id .................... [RUN]
03:51:46  47 of 68 PASS source_not_null_raw_sessions_session_id .......................... [PASS in 0.02s]
03:51:46  48 of 68 START test source_relationships_raw_marketing_attribution_order_id__order_id__source_raw_orders_  [RUN]
03:51:46  48 of 68 PASS source_relationships_raw_marketing_attribution_order_id__order_id__source_raw_orders_  [PASS in 0.03s]
03:51:46  49 of 68 START test source_relationships_raw_marketing_attribution_session_id__session_id__source_raw_sessions_  [RUN]
03:51:46  49 of 68 PASS source_relationships_raw_marketing_attribution_session_id__session_id__source_raw_sessions_  [PASS in 0.04s]
03:51:46  50 of 68 START test source_relationships_raw_order_items_order_id__order_id__source_raw_orders_  [RUN]
03:51:46  50 of 68 PASS source_relationships_raw_order_items_order_id__order_id__source_raw_orders_  [PASS in 0.04s]
03:51:46  51 of 68 START test source_relationships_raw_orders_customer_id__customer_id__source_raw_customers_  [RUN]
03:51:46  51 of 68 PASS source_relationships_raw_orders_customer_id__customer_id__source_raw_customers_  [PASS in 0.03s]
03:51:46  52 of 68 START test source_relationships_raw_payments_order_id__order_id__source_raw_orders_  [RUN]
03:51:46  52 of 68 PASS source_relationships_raw_payments_order_id__order_id__source_raw_orders_  [PASS in 0.03s]
03:51:46  53 of 68 START test source_relationships_raw_refunds_order_id__order_id__source_raw_orders_  [RUN]
03:51:46  53 of 68 PASS source_relationships_raw_refunds_order_id__order_id__source_raw_orders_  [PASS in 0.03s]
03:51:46  54 of 68 START test source_relationships_raw_sessions_customer_id__customer_id__source_raw_customers_  [RUN]
03:51:46  54 of 68 PASS source_relationships_raw_sessions_customer_id__customer_id__source_raw_customers_  [PASS in 0.03s]
03:51:46  55 of 68 START test source_unique_raw_customers_customer_id .................... [RUN]
03:51:46  55 of 68 PASS source_unique_raw_customers_customer_id .......................... [PASS in 0.02s]
03:51:46  56 of 68 START test source_unique_raw_order_items_order_item_id ................ [RUN]
03:51:46  56 of 68 PASS source_unique_raw_order_items_order_item_id ...................... [PASS in 0.04s]
03:51:46  57 of 68 START test source_unique_raw_orders_order_id .......................... [RUN]
03:51:46  57 of 68 PASS source_unique_raw_orders_order_id ................................ [PASS in 0.03s]
03:51:46  58 of 68 START test source_unique_raw_payments_payment_id ...................... [RUN]
03:51:46  58 of 68 PASS source_unique_raw_payments_payment_id ............................ [PASS in 0.03s]
03:51:46  59 of 68 START test source_unique_raw_refunds_refund_id ........................ [RUN]
03:51:46  59 of 68 PASS source_unique_raw_refunds_refund_id .............................. [PASS in 0.02s]
03:51:46  60 of 68 START test source_unique_raw_sessions_session_id ...................... [RUN]
03:51:46  60 of 68 PASS source_unique_raw_sessions_session_id ............................ [PASS in 0.03s]
03:51:46  61 of 68 START test unique_dim_customers_customer_id ........................... [RUN]
03:51:46  61 of 68 PASS unique_dim_customers_customer_id ................................. [PASS in 0.02s]
03:51:46  62 of 68 START test unique_fct_orders_order_id ................................. [RUN]
03:51:46  62 of 68 PASS unique_fct_orders_order_id ....................................... [PASS in 0.04s]
03:51:46  63 of 68 START test unique_int_order_payments_order_id ......................... [RUN]
03:51:46  63 of 68 PASS unique_int_order_payments_order_id ............................... [PASS in 0.03s]
03:51:46  64 of 68 START test unique_int_order_refunds_order_id .......................... [RUN]
03:51:46  64 of 68 PASS unique_int_order_refunds_order_id ................................ [PASS in 0.02s]
03:51:46  65 of 68 START test unique_stg_customers_customer_id ........................... [RUN]
03:51:46  65 of 68 PASS unique_stg_customers_customer_id ................................. [PASS in 0.02s]
03:51:46  66 of 68 START test unique_stg_orders_order_id ................................. [RUN]
03:51:46  66 of 68 PASS unique_stg_orders_order_id ....................................... [PASS in 0.03s]
03:51:46  67 of 68 START test unique_stg_payments_payment_id ............................. [RUN]
03:51:46  67 of 68 PASS unique_stg_payments_payment_id ................................... [PASS in 0.03s]
03:51:46  68 of 68 START test unique_stg_refunds_refund_id ............................... [RUN]
03:51:46  68 of 68 PASS unique_stg_refunds_refund_id ..................................... [PASS in 0.02s]
03:51:46  
03:51:46  Finished running 68 data tests in 0 hours 0 minutes and 2.27 seconds (2.27s).
03:51:47  
03:51:47  Completed successfully
03:51:47  
03:51:47  Done. PASS=68 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=68
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

## make -s dbt-build dbt-test

Started: 2026-09-05T03:51:48Z
Ended: 2026-09-05T03:52:06Z
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
03:51:53  Running with dbt=1.11.14
03:51:53  Registered adapter: clickhouse=1.10.2
03:51:54  Found 8 models, 68 data tests, 7 sources, 536 macros
03:51:54  
03:51:54  Concurrency: 1 threads (target='dev')
03:51:54  
03:51:54  1 of 76 START test source_accepted_values_raw_customers_country__US__DE__GB__TR__BR  [RUN]
03:51:54  1 of 76 PASS source_accepted_values_raw_customers_country__US__DE__GB__TR__BR .. [PASS in 0.07s]
03:51:54  2 of 76 START test source_accepted_values_raw_marketing_attribution_acquisition_channel__organic__paid_search__email__affiliate  [RUN]
03:51:54  2 of 76 PASS source_accepted_values_raw_marketing_attribution_acquisition_channel__organic__paid_search__email__affiliate  [PASS in 0.02s]
03:51:54  3 of 76 START test source_accepted_values_raw_orders_currency__USD__EUR__GBP__TRY  [RUN]
03:51:54  3 of 76 PASS source_accepted_values_raw_orders_currency__USD__EUR__GBP__TRY .... [PASS in 0.02s]
03:51:54  4 of 76 START test source_accepted_values_raw_orders_order_status__completed__cancelled__refunded  [RUN]
03:51:54  4 of 76 PASS source_accepted_values_raw_orders_order_status__completed__cancelled__refunded  [PASS in 0.02s]
03:51:54  5 of 76 START test source_accepted_values_raw_payments_payment_status__succeeded__voided  [RUN]
03:51:55  5 of 76 PASS source_accepted_values_raw_payments_payment_status__succeeded__voided  [PASS in 0.02s]
03:51:55  6 of 76 START test source_accepted_values_raw_refunds_refund_status__succeeded__failed  [RUN]
03:51:55  6 of 76 PASS source_accepted_values_raw_refunds_refund_status__succeeded__failed  [PASS in 0.02s]
03:51:55  7 of 76 START test source_accepted_values_raw_sessions_acquisition_channel__organic__paid_search__email__affiliate  [RUN]
03:51:55  7 of 76 PASS source_accepted_values_raw_sessions_acquisition_channel__organic__paid_search__email__affiliate  [PASS in 0.02s]
03:51:55  8 of 76 START test source_not_null_raw_customers_country ....................... [RUN]
03:51:55  8 of 76 PASS source_not_null_raw_customers_country ............................. [PASS in 0.02s]
03:51:55  9 of 76 START test source_not_null_raw_customers_customer_id ................... [RUN]
03:51:55  9 of 76 PASS source_not_null_raw_customers_customer_id ......................... [PASS in 0.02s]
03:51:55  10 of 76 START test source_not_null_raw_marketing_attribution_attribution_event_id  [RUN]
03:51:55  10 of 76 PASS source_not_null_raw_marketing_attribution_attribution_event_id ... [PASS in 0.02s]
03:51:55  11 of 76 START test source_not_null_raw_marketing_attribution_order_id ......... [RUN]
03:51:55  11 of 76 PASS source_not_null_raw_marketing_attribution_order_id ............... [PASS in 0.02s]
03:51:55  12 of 76 START test source_not_null_raw_marketing_attribution_session_id ....... [RUN]
03:51:55  12 of 76 PASS source_not_null_raw_marketing_attribution_session_id ............. [PASS in 0.02s]
03:51:55  13 of 76 START test source_not_null_raw_order_items_order_id ................... [RUN]
03:51:55  13 of 76 PASS source_not_null_raw_order_items_order_id ......................... [PASS in 0.02s]
03:51:55  14 of 76 START test source_not_null_raw_order_items_order_item_id .............. [RUN]
03:51:55  14 of 76 PASS source_not_null_raw_order_items_order_item_id .................... [PASS in 0.02s]
03:51:55  15 of 76 START test source_not_null_raw_orders_currency ........................ [RUN]
03:51:55  15 of 76 PASS source_not_null_raw_orders_currency .............................. [PASS in 0.02s]
03:51:55  16 of 76 START test source_not_null_raw_orders_customer_id ..................... [RUN]
03:51:55  16 of 76 PASS source_not_null_raw_orders_customer_id ........................... [PASS in 0.02s]
03:51:55  17 of 76 START test source_not_null_raw_orders_order_id ........................ [RUN]
03:51:55  17 of 76 PASS source_not_null_raw_orders_order_id .............................. [PASS in 0.02s]
03:51:55  18 of 76 START test source_not_null_raw_orders_order_status .................... [RUN]
03:51:55  18 of 76 PASS source_not_null_raw_orders_order_status .......................... [PASS in 0.02s]
03:51:55  19 of 76 START test source_not_null_raw_payments_order_id ...................... [RUN]
03:51:55  19 of 76 PASS source_not_null_raw_payments_order_id ............................ [PASS in 0.02s]
03:51:55  20 of 76 START test source_not_null_raw_payments_payment_id .................... [RUN]
03:51:55  20 of 76 PASS source_not_null_raw_payments_payment_id .......................... [PASS in 0.02s]
03:51:55  21 of 76 START test source_not_null_raw_payments_payment_status ................ [RUN]
03:51:55  21 of 76 PASS source_not_null_raw_payments_payment_status ...................... [PASS in 0.02s]
03:51:55  22 of 76 START test source_not_null_raw_refunds_order_id ....................... [RUN]
03:51:55  22 of 76 PASS source_not_null_raw_refunds_order_id ............................. [PASS in 0.02s]
03:51:55  23 of 76 START test source_not_null_raw_refunds_refund_id ...................... [RUN]
03:51:55  23 of 76 PASS source_not_null_raw_refunds_refund_id ............................ [PASS in 0.02s]
03:51:55  24 of 76 START test source_not_null_raw_refunds_refund_status .................. [RUN]
03:51:55  24 of 76 PASS source_not_null_raw_refunds_refund_status ........................ [PASS in 0.02s]
03:51:55  25 of 76 START test source_not_null_raw_sessions_customer_id ................... [RUN]
03:51:55  25 of 76 PASS source_not_null_raw_sessions_customer_id ......................... [PASS in 0.02s]
03:51:55  26 of 76 START test source_not_null_raw_sessions_session_id .................... [RUN]
03:51:55  26 of 76 PASS source_not_null_raw_sessions_session_id .......................... [PASS in 0.02s]
03:51:55  27 of 76 START test source_relationships_raw_marketing_attribution_order_id__order_id__source_raw_orders_  [RUN]
03:51:55  27 of 76 PASS source_relationships_raw_marketing_attribution_order_id__order_id__source_raw_orders_  [PASS in 0.05s]
03:51:55  28 of 76 START test source_relationships_raw_marketing_attribution_session_id__session_id__source_raw_sessions_  [RUN]
03:51:55  28 of 76 PASS source_relationships_raw_marketing_attribution_session_id__session_id__source_raw_sessions_  [PASS in 0.05s]
03:51:55  29 of 76 START test source_relationships_raw_order_items_order_id__order_id__source_raw_orders_  [RUN]
03:51:55  29 of 76 PASS source_relationships_raw_order_items_order_id__order_id__source_raw_orders_  [PASS in 0.04s]
03:51:55  30 of 76 START test source_relationships_raw_orders_customer_id__customer_id__source_raw_customers_  [RUN]
03:51:55  30 of 76 PASS source_relationships_raw_orders_customer_id__customer_id__source_raw_customers_  [PASS in 0.03s]
03:51:55  31 of 76 START test source_relationships_raw_payments_order_id__order_id__source_raw_orders_  [RUN]
03:51:55  31 of 76 PASS source_relationships_raw_payments_order_id__order_id__source_raw_orders_  [PASS in 0.04s]
03:51:55  32 of 76 START test source_relationships_raw_refunds_order_id__order_id__source_raw_orders_  [RUN]
03:51:55  32 of 76 PASS source_relationships_raw_refunds_order_id__order_id__source_raw_orders_  [PASS in 0.04s]
03:51:55  33 of 76 START test source_relationships_raw_sessions_customer_id__customer_id__source_raw_customers_  [RUN]
03:51:55  33 of 76 PASS source_relationships_raw_sessions_customer_id__customer_id__source_raw_customers_  [PASS in 0.03s]
03:51:55  34 of 76 START test source_unique_raw_customers_customer_id .................... [RUN]
03:51:55  34 of 76 PASS source_unique_raw_customers_customer_id .......................... [PASS in 0.03s]
03:51:55  35 of 76 START test source_unique_raw_order_items_order_item_id ................ [RUN]
03:51:55  35 of 76 PASS source_unique_raw_order_items_order_item_id ...................... [PASS in 0.04s]
03:51:55  36 of 76 START test source_unique_raw_orders_order_id .......................... [RUN]
03:51:55  36 of 76 PASS source_unique_raw_orders_order_id ................................ [PASS in 0.03s]
03:51:55  37 of 76 START test source_unique_raw_payments_payment_id ...................... [RUN]
03:51:55  37 of 76 PASS source_unique_raw_payments_payment_id ............................ [PASS in 0.03s]
03:51:55  38 of 76 START test source_unique_raw_refunds_refund_id ........................ [RUN]
03:51:55  38 of 76 PASS source_unique_raw_refunds_refund_id .............................. [PASS in 0.02s]
03:51:55  39 of 76 START test source_unique_raw_sessions_session_id ...................... [RUN]
03:51:55  39 of 76 PASS source_unique_raw_sessions_session_id ............................ [PASS in 0.03s]
03:51:55  40 of 76 START sql view model `analytics`.`stg_customers` ...................... [RUN]
03:51:56  40 of 76 OK created sql view model `analytics`.`stg_customers` ................. [OK in 0.13s]
03:51:56  41 of 76 START sql view model `analytics`.`stg_orders` ......................... [RUN]
03:51:56  41 of 76 OK created sql view model `analytics`.`stg_orders` .................... [OK in 0.04s]
03:51:56  42 of 76 START sql view model `analytics`.`stg_payments` ....................... [RUN]
03:51:56  42 of 76 OK created sql view model `analytics`.`stg_payments` .................. [OK in 0.05s]
03:51:56  43 of 76 START sql view model `analytics`.`stg_refunds` ........................ [RUN]
03:51:56  43 of 76 OK created sql view model `analytics`.`stg_refunds` ................... [OK in 0.04s]
03:51:56  44 of 76 START test not_null_stg_customers_customer_id ......................... [RUN]
03:51:56  44 of 76 PASS not_null_stg_customers_customer_id ............................... [PASS in 0.02s]
03:51:56  45 of 76 START test unique_stg_customers_customer_id ........................... [RUN]
03:51:56  45 of 76 PASS unique_stg_customers_customer_id ................................. [PASS in 0.02s]
03:51:56  46 of 76 START test not_null_stg_orders_order_id ............................... [RUN]
03:51:56  46 of 76 PASS not_null_stg_orders_order_id ..................................... [PASS in 0.02s]
03:51:56  47 of 76 START test unique_stg_orders_order_id ................................. [RUN]
03:51:56  47 of 76 PASS unique_stg_orders_order_id ....................................... [PASS in 0.04s]
03:51:56  48 of 76 START test not_null_stg_payments_payment_id ........................... [RUN]
03:51:56  48 of 76 PASS not_null_stg_payments_payment_id ................................. [PASS in 0.02s]
03:51:56  49 of 76 START test unique_stg_payments_payment_id ............................. [RUN]
03:51:56  49 of 76 PASS unique_stg_payments_payment_id ................................... [PASS in 0.03s]
03:51:56  50 of 76 START test not_null_stg_refunds_refund_id ............................. [RUN]
03:51:56  50 of 76 PASS not_null_stg_refunds_refund_id ................................... [PASS in 0.02s]
03:51:56  51 of 76 START test unique_stg_refunds_refund_id ............................... [RUN]
03:51:56  51 of 76 PASS unique_stg_refunds_refund_id ..................................... [PASS in 0.02s]
03:51:56  52 of 76 START sql table model `analytics`.`dim_customers` ..................... [RUN]
03:51:56  52 of 76 OK created sql table model `analytics`.`dim_customers` ................ [OK in 0.23s]
03:51:56  53 of 76 START sql view model `analytics`.`int_order_payments` ................. [RUN]
03:51:56  53 of 76 OK created sql view model `analytics`.`int_order_payments` ............ [OK in 0.04s]
03:51:56  54 of 76 START sql view model `analytics`.`int_order_refunds` .................. [RUN]
03:51:56  54 of 76 OK created sql view model `analytics`.`int_order_refunds` ............. [OK in 0.05s]
03:51:56  55 of 76 START test not_null_dim_customers_customer_id ......................... [RUN]
03:51:56  55 of 76 PASS not_null_dim_customers_customer_id ............................... [PASS in 0.02s]
03:51:56  56 of 76 START test unique_dim_customers_customer_id ........................... [RUN]
03:51:56  56 of 76 PASS unique_dim_customers_customer_id ................................. [PASS in 0.02s]
03:51:56  57 of 76 START test not_null_int_order_payments_order_id ....................... [RUN]
03:51:56  57 of 76 PASS not_null_int_order_payments_order_id ............................. [PASS in 0.02s]
03:51:56  58 of 76 START test not_null_int_order_payments_successful_payment_amount_cents  [RUN]
03:51:56  58 of 76 PASS not_null_int_order_payments_successful_payment_amount_cents ...... [PASS in 0.02s]
03:51:56  59 of 76 START test not_null_int_order_payments_successful_payment_count ....... [RUN]
03:51:56  59 of 76 PASS not_null_int_order_payments_successful_payment_count ............. [PASS in 0.02s]
03:51:56  60 of 76 START test unique_int_order_payments_order_id ......................... [RUN]
03:51:56  60 of 76 PASS unique_int_order_payments_order_id ............................... [PASS in 0.03s]
03:51:56  61 of 76 START test not_null_int_order_refunds_order_id ........................ [RUN]
03:51:56  61 of 76 PASS not_null_int_order_refunds_order_id .............................. [PASS in 0.02s]
03:51:56  62 of 76 START test not_null_int_order_refunds_successful_refund_amount_cents .. [RUN]
03:51:56  62 of 76 PASS not_null_int_order_refunds_successful_refund_amount_cents ........ [PASS in 0.02s]
03:51:56  63 of 76 START test not_null_int_order_refunds_successful_refund_count ......... [RUN]
03:51:57  63 of 76 PASS not_null_int_order_refunds_successful_refund_count ............... [PASS in 0.02s]
03:51:57  64 of 76 START test unique_int_order_refunds_order_id .......................... [RUN]
03:51:57  64 of 76 PASS unique_int_order_refunds_order_id ................................ [PASS in 0.02s]
03:51:57  65 of 76 START sql table model `analytics`.`fct_orders` ........................ [RUN]
03:51:57  65 of 76 OK created sql table model `analytics`.`fct_orders` ................... [OK in 0.26s]
03:51:57  66 of 76 START test accepted_values_fct_orders_order_status__completed__cancelled__refunded  [RUN]
03:51:57  66 of 76 PASS accepted_values_fct_orders_order_status__completed__cancelled__refunded  [PASS in 0.02s]
03:51:57  67 of 76 START test assert_cancelled_orders_are_unpaid ......................... [RUN]
03:51:57  67 of 76 PASS assert_cancelled_orders_are_unpaid ............................... [PASS in 0.02s]
03:51:57  68 of 76 START test assert_fct_orders_matches_source_count ..................... [RUN]
03:51:57  68 of 76 PASS assert_fct_orders_matches_source_count ........................... [PASS in 0.03s]
03:51:57  69 of 76 START test assert_refunds_do_not_exceed_payments ...................... [RUN]
03:51:57  69 of 76 PASS assert_refunds_do_not_exceed_payments ............................ [PASS in 0.02s]
03:51:57  70 of 76 START test assert_successful_payments_match_orders .................... [RUN]
03:51:57  70 of 76 PASS assert_successful_payments_match_orders .......................... [PASS in 0.02s]
03:51:57  71 of 76 START test not_null_fct_orders_customer_id ............................ [RUN]
03:51:57  71 of 76 PASS not_null_fct_orders_customer_id .................................. [PASS in 0.02s]
03:51:57  72 of 76 START test not_null_fct_orders_order_id ............................... [RUN]
03:51:57  72 of 76 PASS not_null_fct_orders_order_id ..................................... [PASS in 0.02s]
03:51:57  73 of 76 START test not_null_fct_orders_successful_payment_amount_cents ........ [RUN]
03:51:57  73 of 76 PASS not_null_fct_orders_successful_payment_amount_cents .............. [PASS in 0.02s]
03:51:57  74 of 76 START test not_null_fct_orders_successful_refund_amount_cents ......... [RUN]
03:51:57  74 of 76 PASS not_null_fct_orders_successful_refund_amount_cents ............... [PASS in 0.02s]
03:51:57  75 of 76 START test relationships_fct_orders_customer_id__customer_id__ref_dim_customers_  [RUN]
03:51:57  75 of 76 PASS relationships_fct_orders_customer_id__customer_id__ref_dim_customers_  [PASS in 0.03s]
03:51:57  76 of 76 START test unique_fct_orders_order_id ................................. [RUN]
03:51:57  76 of 76 PASS unique_fct_orders_order_id ....................................... [PASS in 0.03s]
03:51:57  
03:51:57  Finished running 2 table models, 68 data tests, 6 view models in 0 hours 0 minutes and 3.24 seconds (3.24s).
03:51:57  
03:51:57  Completed successfully
03:51:57  
03:51:57  Done. PASS=76 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=76
03:52:02  Running with dbt=1.11.14
03:52:02  Registered adapter: clickhouse=1.10.2
03:52:03  Found 8 models, 68 data tests, 7 sources, 536 macros
03:52:03  
03:52:03  Concurrency: 1 threads (target='dev')
03:52:03  
03:52:03  1 of 68 START test accepted_values_fct_orders_order_status__completed__cancelled__refunded  [RUN]
03:52:03  1 of 68 PASS accepted_values_fct_orders_order_status__completed__cancelled__refunded  [PASS in 0.08s]
03:52:03  2 of 68 START test assert_cancelled_orders_are_unpaid .......................... [RUN]
03:52:04  2 of 68 PASS assert_cancelled_orders_are_unpaid ................................ [PASS in 0.02s]
03:52:04  3 of 68 START test assert_fct_orders_matches_source_count ...................... [RUN]
03:52:04  3 of 68 PASS assert_fct_orders_matches_source_count ............................ [PASS in 0.02s]
03:52:04  4 of 68 START test assert_refunds_do_not_exceed_payments ....................... [RUN]
03:52:04  4 of 68 PASS assert_refunds_do_not_exceed_payments ............................. [PASS in 0.02s]
03:52:04  5 of 68 START test assert_successful_payments_match_orders ..................... [RUN]
03:52:04  5 of 68 PASS assert_successful_payments_match_orders ........................... [PASS in 0.03s]
03:52:04  6 of 68 START test not_null_dim_customers_customer_id .......................... [RUN]
03:52:04  6 of 68 PASS not_null_dim_customers_customer_id ................................ [PASS in 0.03s]
03:52:04  7 of 68 START test not_null_fct_orders_customer_id ............................. [RUN]
03:52:04  7 of 68 PASS not_null_fct_orders_customer_id ................................... [PASS in 0.02s]
03:52:04  8 of 68 START test not_null_fct_orders_order_id ................................ [RUN]
03:52:04  8 of 68 PASS not_null_fct_orders_order_id ...................................... [PASS in 0.02s]
03:52:04  9 of 68 START test not_null_fct_orders_successful_payment_amount_cents ......... [RUN]
03:52:04  9 of 68 PASS not_null_fct_orders_successful_payment_amount_cents ............... [PASS in 0.02s]
03:52:04  10 of 68 START test not_null_fct_orders_successful_refund_amount_cents ......... [RUN]
03:52:04  10 of 68 PASS not_null_fct_orders_successful_refund_amount_cents ............... [PASS in 0.02s]
03:52:04  11 of 68 START test not_null_int_order_payments_order_id ....................... [RUN]
03:52:04  11 of 68 PASS not_null_int_order_payments_order_id ............................. [PASS in 0.03s]
03:52:04  12 of 68 START test not_null_int_order_payments_successful_payment_amount_cents  [RUN]
03:52:04  12 of 68 PASS not_null_int_order_payments_successful_payment_amount_cents ...... [PASS in 0.03s]
03:52:04  13 of 68 START test not_null_int_order_payments_successful_payment_count ....... [RUN]
03:52:04  13 of 68 PASS not_null_int_order_payments_successful_payment_count ............. [PASS in 0.03s]
03:52:04  14 of 68 START test not_null_int_order_refunds_order_id ........................ [RUN]
03:52:04  14 of 68 PASS not_null_int_order_refunds_order_id .............................. [PASS in 0.02s]
03:52:04  15 of 68 START test not_null_int_order_refunds_successful_refund_amount_cents .. [RUN]
03:52:04  15 of 68 PASS not_null_int_order_refunds_successful_refund_amount_cents ........ [PASS in 0.03s]
03:52:04  16 of 68 START test not_null_int_order_refunds_successful_refund_count ......... [RUN]
03:52:04  16 of 68 PASS not_null_int_order_refunds_successful_refund_count ............... [PASS in 0.03s]
03:52:04  17 of 68 START test not_null_stg_customers_customer_id ......................... [RUN]
03:52:04  17 of 68 PASS not_null_stg_customers_customer_id ............................... [PASS in 0.02s]
03:52:04  18 of 68 START test not_null_stg_orders_order_id ............................... [RUN]
03:52:04  18 of 68 PASS not_null_stg_orders_order_id ..................................... [PASS in 0.03s]
03:52:04  19 of 68 START test not_null_stg_payments_payment_id ........................... [RUN]
03:52:04  19 of 68 PASS not_null_stg_payments_payment_id ................................. [PASS in 0.02s]
03:52:04  20 of 68 START test not_null_stg_refunds_refund_id ............................. [RUN]
03:52:04  20 of 68 PASS not_null_stg_refunds_refund_id ................................... [PASS in 0.02s]
03:52:04  21 of 68 START test relationships_fct_orders_customer_id__customer_id__ref_dim_customers_  [RUN]
03:52:04  21 of 68 PASS relationships_fct_orders_customer_id__customer_id__ref_dim_customers_  [PASS in 0.04s]
03:52:04  22 of 68 START test source_accepted_values_raw_customers_country__US__DE__GB__TR__BR  [RUN]
03:52:04  22 of 68 PASS source_accepted_values_raw_customers_country__US__DE__GB__TR__BR . [PASS in 0.03s]
03:52:04  23 of 68 START test source_accepted_values_raw_marketing_attribution_acquisition_channel__organic__paid_search__email__affiliate  [RUN]
03:52:04  23 of 68 PASS source_accepted_values_raw_marketing_attribution_acquisition_channel__organic__paid_search__email__affiliate  [PASS in 0.03s]
03:52:04  24 of 68 START test source_accepted_values_raw_orders_currency__USD__EUR__GBP__TRY  [RUN]
03:52:04  24 of 68 PASS source_accepted_values_raw_orders_currency__USD__EUR__GBP__TRY ... [PASS in 0.03s]
03:52:04  25 of 68 START test source_accepted_values_raw_orders_order_status__completed__cancelled__refunded  [RUN]
03:52:04  25 of 68 PASS source_accepted_values_raw_orders_order_status__completed__cancelled__refunded  [PASS in 0.03s]
03:52:04  26 of 68 START test source_accepted_values_raw_payments_payment_status__succeeded__voided  [RUN]
03:52:04  26 of 68 PASS source_accepted_values_raw_payments_payment_status__succeeded__voided  [PASS in 0.03s]
03:52:04  27 of 68 START test source_accepted_values_raw_refunds_refund_status__succeeded__failed  [RUN]
03:52:04  27 of 68 PASS source_accepted_values_raw_refunds_refund_status__succeeded__failed  [PASS in 0.03s]
03:52:04  28 of 68 START test source_accepted_values_raw_sessions_acquisition_channel__organic__paid_search__email__affiliate  [RUN]
03:52:04  28 of 68 PASS source_accepted_values_raw_sessions_acquisition_channel__organic__paid_search__email__affiliate  [PASS in 0.03s]
03:52:04  29 of 68 START test source_not_null_raw_customers_country ...................... [RUN]
03:52:04  29 of 68 PASS source_not_null_raw_customers_country ............................ [PASS in 0.03s]
03:52:04  30 of 68 START test source_not_null_raw_customers_customer_id .................. [RUN]
03:52:04  30 of 68 PASS source_not_null_raw_customers_customer_id ........................ [PASS in 0.02s]
03:52:04  31 of 68 START test source_not_null_raw_marketing_attribution_attribution_event_id  [RUN]
03:52:04  31 of 68 PASS source_not_null_raw_marketing_attribution_attribution_event_id ... [PASS in 0.05s]
03:52:04  32 of 68 START test source_not_null_raw_marketing_attribution_order_id ......... [RUN]
03:52:04  32 of 68 PASS source_not_null_raw_marketing_attribution_order_id ............... [PASS in 0.02s]
03:52:04  33 of 68 START test source_not_null_raw_marketing_attribution_session_id ....... [RUN]
03:52:04  33 of 68 PASS source_not_null_raw_marketing_attribution_session_id ............. [PASS in 0.02s]
03:52:04  34 of 68 START test source_not_null_raw_order_items_order_id ................... [RUN]
03:52:04  34 of 68 PASS source_not_null_raw_order_items_order_id ......................... [PASS in 0.02s]
03:52:04  35 of 68 START test source_not_null_raw_order_items_order_item_id .............. [RUN]
03:52:05  35 of 68 PASS source_not_null_raw_order_items_order_item_id .................... [PASS in 0.02s]
03:52:05  36 of 68 START test source_not_null_raw_orders_currency ........................ [RUN]
03:52:05  36 of 68 PASS source_not_null_raw_orders_currency .............................. [PASS in 0.02s]
03:52:05  37 of 68 START test source_not_null_raw_orders_customer_id ..................... [RUN]
03:52:05  37 of 68 PASS source_not_null_raw_orders_customer_id ........................... [PASS in 0.02s]
03:52:05  38 of 68 START test source_not_null_raw_orders_order_id ........................ [RUN]
03:52:05  38 of 68 PASS source_not_null_raw_orders_order_id .............................. [PASS in 0.02s]
03:52:05  39 of 68 START test source_not_null_raw_orders_order_status .................... [RUN]
03:52:05  39 of 68 PASS source_not_null_raw_orders_order_status .......................... [PASS in 0.02s]
03:52:05  40 of 68 START test source_not_null_raw_payments_order_id ...................... [RUN]
03:52:05  40 of 68 PASS source_not_null_raw_payments_order_id ............................ [PASS in 0.02s]
03:52:05  41 of 68 START test source_not_null_raw_payments_payment_id .................... [RUN]
03:52:05  41 of 68 PASS source_not_null_raw_payments_payment_id .......................... [PASS in 0.02s]
03:52:05  42 of 68 START test source_not_null_raw_payments_payment_status ................ [RUN]
03:52:05  42 of 68 PASS source_not_null_raw_payments_payment_status ...................... [PASS in 0.02s]
03:52:05  43 of 68 START test source_not_null_raw_refunds_order_id ....................... [RUN]
03:52:05  43 of 68 PASS source_not_null_raw_refunds_order_id ............................. [PASS in 0.02s]
03:52:05  44 of 68 START test source_not_null_raw_refunds_refund_id ...................... [RUN]
03:52:05  44 of 68 PASS source_not_null_raw_refunds_refund_id ............................ [PASS in 0.02s]
03:52:05  45 of 68 START test source_not_null_raw_refunds_refund_status .................. [RUN]
03:52:05  45 of 68 PASS source_not_null_raw_refunds_refund_status ........................ [PASS in 0.02s]
03:52:05  46 of 68 START test source_not_null_raw_sessions_customer_id ................... [RUN]
03:52:05  46 of 68 PASS source_not_null_raw_sessions_customer_id ......................... [PASS in 0.02s]
03:52:05  47 of 68 START test source_not_null_raw_sessions_session_id .................... [RUN]
03:52:05  47 of 68 PASS source_not_null_raw_sessions_session_id .......................... [PASS in 0.02s]
03:52:05  48 of 68 START test source_relationships_raw_marketing_attribution_order_id__order_id__source_raw_orders_  [RUN]
03:52:05  48 of 68 PASS source_relationships_raw_marketing_attribution_order_id__order_id__source_raw_orders_  [PASS in 0.04s]
03:52:05  49 of 68 START test source_relationships_raw_marketing_attribution_session_id__session_id__source_raw_sessions_  [RUN]
03:52:05  49 of 68 PASS source_relationships_raw_marketing_attribution_session_id__session_id__source_raw_sessions_  [PASS in 0.05s]
03:52:05  50 of 68 START test source_relationships_raw_order_items_order_id__order_id__source_raw_orders_  [RUN]
03:52:05  50 of 68 PASS source_relationships_raw_order_items_order_id__order_id__source_raw_orders_  [PASS in 0.05s]
03:52:05  51 of 68 START test source_relationships_raw_orders_customer_id__customer_id__source_raw_customers_  [RUN]
03:52:05  51 of 68 PASS source_relationships_raw_orders_customer_id__customer_id__source_raw_customers_  [PASS in 0.03s]
03:52:05  52 of 68 START test source_relationships_raw_payments_order_id__order_id__source_raw_orders_  [RUN]
03:52:05  52 of 68 PASS source_relationships_raw_payments_order_id__order_id__source_raw_orders_  [PASS in 0.04s]
03:52:05  53 of 68 START test source_relationships_raw_refunds_order_id__order_id__source_raw_orders_  [RUN]
03:52:05  53 of 68 PASS source_relationships_raw_refunds_order_id__order_id__source_raw_orders_  [PASS in 0.03s]
03:52:05  54 of 68 START test source_relationships_raw_sessions_customer_id__customer_id__source_raw_customers_  [RUN]
03:52:05  54 of 68 PASS source_relationships_raw_sessions_customer_id__customer_id__source_raw_customers_  [PASS in 0.03s]
03:52:05  55 of 68 START test source_unique_raw_customers_customer_id .................... [RUN]
03:52:05  55 of 68 PASS source_unique_raw_customers_customer_id .......................... [PASS in 0.03s]
03:52:05  56 of 68 START test source_unique_raw_order_items_order_item_id ................ [RUN]
03:52:05  56 of 68 PASS source_unique_raw_order_items_order_item_id ...................... [PASS in 0.04s]
03:52:05  57 of 68 START test source_unique_raw_orders_order_id .......................... [RUN]
03:52:05  57 of 68 PASS source_unique_raw_orders_order_id ................................ [PASS in 0.04s]
03:52:05  58 of 68 START test source_unique_raw_payments_payment_id ...................... [RUN]
03:52:05  58 of 68 PASS source_unique_raw_payments_payment_id ............................ [PASS in 0.03s]
03:52:05  59 of 68 START test source_unique_raw_refunds_refund_id ........................ [RUN]
03:52:05  59 of 68 PASS source_unique_raw_refunds_refund_id .............................. [PASS in 0.02s]
03:52:05  60 of 68 START test source_unique_raw_sessions_session_id ...................... [RUN]
03:52:05  60 of 68 PASS source_unique_raw_sessions_session_id ............................ [PASS in 0.03s]
03:52:05  61 of 68 START test unique_dim_customers_customer_id ........................... [RUN]
03:52:05  61 of 68 PASS unique_dim_customers_customer_id ................................. [PASS in 0.02s]
03:52:05  62 of 68 START test unique_fct_orders_order_id ................................. [RUN]
03:52:05  62 of 68 PASS unique_fct_orders_order_id ....................................... [PASS in 0.04s]
03:52:05  63 of 68 START test unique_int_order_payments_order_id ......................... [RUN]
03:52:05  63 of 68 PASS unique_int_order_payments_order_id ............................... [PASS in 0.04s]
03:52:05  64 of 68 START test unique_int_order_refunds_order_id .......................... [RUN]
03:52:05  64 of 68 PASS unique_int_order_refunds_order_id ................................ [PASS in 0.02s]
03:52:05  65 of 68 START test unique_stg_customers_customer_id ........................... [RUN]
03:52:05  65 of 68 PASS unique_stg_customers_customer_id ................................. [PASS in 0.02s]
03:52:05  66 of 68 START test unique_stg_orders_order_id ................................. [RUN]
03:52:06  66 of 68 PASS unique_stg_orders_order_id ....................................... [PASS in 0.04s]
03:52:06  67 of 68 START test unique_stg_payments_payment_id ............................. [RUN]
03:52:06  67 of 68 PASS unique_stg_payments_payment_id ................................... [PASS in 0.03s]
03:52:06  68 of 68 START test unique_stg_refunds_refund_id ............................... [RUN]
03:52:06  68 of 68 PASS unique_stg_refunds_refund_id ..................................... [PASS in 0.02s]
03:52:06  
03:52:06  Finished running 68 data tests in 0 hours 0 minutes and 2.72 seconds (2.72s).
03:52:06  
03:52:06  Completed successfully
03:52:06  
03:52:06  Done. PASS=68 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=68
```

## make -s seed dbt-build dbt-test clickhouse-test dbt-baseline-test

Started: 2026-09-05T03:52:06Z
Ended: 2026-09-05T03:52:33Z
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
#1 DONE 0.1s

#2 [dbt internal] load metadata for docker.io/library/python:3.12.14-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254
#2 DONE 0.1s

#3 [dbt internal] load .dockerignore
#3 transferring context: 73B done
#3 DONE 0.1s

#4 [dbt 1/5] FROM docker.io/library/python:3.12.14-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254
#4 DONE 0.0s

#5 [dbt internal] load build context
#5 transferring context: 40B done
#5 DONE 0.0s

#6 [dbt 2/5] RUN apt-get update     && apt-get install --yes --no-install-recommends git     && rm -rf /var/lib/apt/lists/*     && groupadd --gid 1000 dbt     && useradd --uid 1000 --gid 1000 --create-home dbt
#6 CACHED

#7 [dbt 3/5] COPY requirements.lock /tmp/requirements.lock
#7 CACHED

#8 [dbt 4/5] RUN python -m pip install --requirement /tmp/requirements.lock
#8 CACHED

#9 [dbt 5/5] WORKDIR /workspace
#9 CACHED

#10 [dbt] exporting to image
#10 exporting layers done
#10 writing image sha256:299b4b00e44db396a107eb575511d0f20b40c7120d8c9f5bed85f2dbd68a345b 0.0s done
#10 naming to docker.io/library/agentic-data-platform-dbt:1.11.14-1.10.2 0.0s done
#10 DONE 0.1s

#11 [dbt] resolving provenance for metadata file
 dbt  Built
#11 DONE 0.0s
03:52:13  Running with dbt=1.11.14
03:52:13  Registered adapter: clickhouse=1.10.2
03:52:14  Found 8 models, 68 data tests, 7 sources, 536 macros
03:52:14  
03:52:14  Concurrency: 1 threads (target='dev')
03:52:14  
03:52:14  1 of 76 START test source_accepted_values_raw_customers_country__US__DE__GB__TR__BR  [RUN]
03:52:15  1 of 76 PASS source_accepted_values_raw_customers_country__US__DE__GB__TR__BR .. [PASS in 0.09s]
03:52:15  2 of 76 START test source_accepted_values_raw_marketing_attribution_acquisition_channel__organic__paid_search__email__affiliate  [RUN]
03:52:15  2 of 76 PASS source_accepted_values_raw_marketing_attribution_acquisition_channel__organic__paid_search__email__affiliate  [PASS in 0.06s]
03:52:15  3 of 76 START test source_accepted_values_raw_orders_currency__USD__EUR__GBP__TRY  [RUN]
03:52:15  3 of 76 PASS source_accepted_values_raw_orders_currency__USD__EUR__GBP__TRY .... [PASS in 0.04s]
03:52:15  4 of 76 START test source_accepted_values_raw_orders_order_status__completed__cancelled__refunded  [RUN]
03:52:15  4 of 76 PASS source_accepted_values_raw_orders_order_status__completed__cancelled__refunded  [PASS in 0.03s]
03:52:15  5 of 76 START test source_accepted_values_raw_payments_payment_status__succeeded__voided  [RUN]
03:52:15  5 of 76 PASS source_accepted_values_raw_payments_payment_status__succeeded__voided  [PASS in 0.02s]
03:52:15  6 of 76 START test source_accepted_values_raw_refunds_refund_status__succeeded__failed  [RUN]
03:52:15  6 of 76 PASS source_accepted_values_raw_refunds_refund_status__succeeded__failed  [PASS in 0.03s]
03:52:15  7 of 76 START test source_accepted_values_raw_sessions_acquisition_channel__organic__paid_search__email__affiliate  [RUN]
03:52:15  7 of 76 PASS source_accepted_values_raw_sessions_acquisition_channel__organic__paid_search__email__affiliate  [PASS in 0.02s]
03:52:15  8 of 76 START test source_not_null_raw_customers_country ....................... [RUN]
03:52:15  8 of 76 PASS source_not_null_raw_customers_country ............................. [PASS in 0.03s]
03:52:15  9 of 76 START test source_not_null_raw_customers_customer_id ................... [RUN]
03:52:15  9 of 76 PASS source_not_null_raw_customers_customer_id ......................... [PASS in 0.02s]
03:52:15  10 of 76 START test source_not_null_raw_marketing_attribution_attribution_event_id  [RUN]
03:52:15  10 of 76 PASS source_not_null_raw_marketing_attribution_attribution_event_id ... [PASS in 0.02s]
03:52:15  11 of 76 START test source_not_null_raw_marketing_attribution_order_id ......... [RUN]
03:52:15  11 of 76 PASS source_not_null_raw_marketing_attribution_order_id ............... [PASS in 0.02s]
03:52:15  12 of 76 START test source_not_null_raw_marketing_attribution_session_id ....... [RUN]
03:52:15  12 of 76 PASS source_not_null_raw_marketing_attribution_session_id ............. [PASS in 0.03s]
03:52:15  13 of 76 START test source_not_null_raw_order_items_order_id ................... [RUN]
03:52:15  13 of 76 PASS source_not_null_raw_order_items_order_id ......................... [PASS in 0.03s]
03:52:15  14 of 76 START test source_not_null_raw_order_items_order_item_id .............. [RUN]
03:52:15  14 of 76 PASS source_not_null_raw_order_items_order_item_id .................... [PASS in 0.03s]
03:52:15  15 of 76 START test source_not_null_raw_orders_currency ........................ [RUN]
03:52:15  15 of 76 PASS source_not_null_raw_orders_currency .............................. [PASS in 0.03s]
03:52:15  16 of 76 START test source_not_null_raw_orders_customer_id ..................... [RUN]
03:52:15  16 of 76 PASS source_not_null_raw_orders_customer_id ........................... [PASS in 0.03s]
03:52:15  17 of 76 START test source_not_null_raw_orders_order_id ........................ [RUN]
03:52:15  17 of 76 PASS source_not_null_raw_orders_order_id .............................. [PASS in 0.03s]
03:52:15  18 of 76 START test source_not_null_raw_orders_order_status .................... [RUN]
03:52:15  18 of 76 PASS source_not_null_raw_orders_order_status .......................... [PASS in 0.02s]
03:52:15  19 of 76 START test source_not_null_raw_payments_order_id ...................... [RUN]
03:52:15  19 of 76 PASS source_not_null_raw_payments_order_id ............................ [PASS in 0.02s]
03:52:15  20 of 76 START test source_not_null_raw_payments_payment_id .................... [RUN]
03:52:15  20 of 76 PASS source_not_null_raw_payments_payment_id .......................... [PASS in 0.02s]
03:52:15  21 of 76 START test source_not_null_raw_payments_payment_status ................ [RUN]
03:52:15  21 of 76 PASS source_not_null_raw_payments_payment_status ...................... [PASS in 0.02s]
03:52:15  22 of 76 START test source_not_null_raw_refunds_order_id ....................... [RUN]
03:52:15  22 of 76 PASS source_not_null_raw_refunds_order_id ............................. [PASS in 0.02s]
03:52:15  23 of 76 START test source_not_null_raw_refunds_refund_id ...................... [RUN]
03:52:15  23 of 76 PASS source_not_null_raw_refunds_refund_id ............................ [PASS in 0.03s]
03:52:15  24 of 76 START test source_not_null_raw_refunds_refund_status .................. [RUN]
03:52:15  24 of 76 PASS source_not_null_raw_refunds_refund_status ........................ [PASS in 0.03s]
03:52:15  25 of 76 START test source_not_null_raw_sessions_customer_id ................... [RUN]
03:52:15  25 of 76 PASS source_not_null_raw_sessions_customer_id ......................... [PASS in 0.02s]
03:52:15  26 of 76 START test source_not_null_raw_sessions_session_id .................... [RUN]
03:52:15  26 of 76 PASS source_not_null_raw_sessions_session_id .......................... [PASS in 0.02s]
03:52:15  27 of 76 START test source_relationships_raw_marketing_attribution_order_id__order_id__source_raw_orders_  [RUN]
03:52:15  27 of 76 PASS source_relationships_raw_marketing_attribution_order_id__order_id__source_raw_orders_  [PASS in 0.04s]
03:52:15  28 of 76 START test source_relationships_raw_marketing_attribution_session_id__session_id__source_raw_sessions_  [RUN]
03:52:15  28 of 76 PASS source_relationships_raw_marketing_attribution_session_id__session_id__source_raw_sessions_  [PASS in 0.05s]
03:52:15  29 of 76 START test source_relationships_raw_order_items_order_id__order_id__source_raw_orders_  [RUN]
03:52:15  29 of 76 PASS source_relationships_raw_order_items_order_id__order_id__source_raw_orders_  [PASS in 0.05s]
03:52:15  30 of 76 START test source_relationships_raw_orders_customer_id__customer_id__source_raw_customers_  [RUN]
03:52:16  30 of 76 PASS source_relationships_raw_orders_customer_id__customer_id__source_raw_customers_  [PASS in 0.04s]
03:52:16  31 of 76 START test source_relationships_raw_payments_order_id__order_id__source_raw_orders_  [RUN]
03:52:16  31 of 76 PASS source_relationships_raw_payments_order_id__order_id__source_raw_orders_  [PASS in 0.04s]
03:52:16  32 of 76 START test source_relationships_raw_refunds_order_id__order_id__source_raw_orders_  [RUN]
03:52:16  32 of 76 PASS source_relationships_raw_refunds_order_id__order_id__source_raw_orders_  [PASS in 0.03s]
03:52:16  33 of 76 START test source_relationships_raw_sessions_customer_id__customer_id__source_raw_customers_  [RUN]
03:52:16  33 of 76 PASS source_relationships_raw_sessions_customer_id__customer_id__source_raw_customers_  [PASS in 0.03s]
03:52:16  34 of 76 START test source_unique_raw_customers_customer_id .................... [RUN]
03:52:16  34 of 76 PASS source_unique_raw_customers_customer_id .......................... [PASS in 0.03s]
03:52:16  35 of 76 START test source_unique_raw_order_items_order_item_id ................ [RUN]
03:52:16  35 of 76 PASS source_unique_raw_order_items_order_item_id ...................... [PASS in 0.06s]
03:52:16  36 of 76 START test source_unique_raw_orders_order_id .......................... [RUN]
03:52:16  36 of 76 PASS source_unique_raw_orders_order_id ................................ [PASS in 0.04s]
03:52:16  37 of 76 START test source_unique_raw_payments_payment_id ...................... [RUN]
03:52:16  37 of 76 PASS source_unique_raw_payments_payment_id ............................ [PASS in 0.04s]
03:52:16  38 of 76 START test source_unique_raw_refunds_refund_id ........................ [RUN]
03:52:16  38 of 76 PASS source_unique_raw_refunds_refund_id .............................. [PASS in 0.02s]
03:52:16  39 of 76 START test source_unique_raw_sessions_session_id ...................... [RUN]
03:52:16  39 of 76 PASS source_unique_raw_sessions_session_id ............................ [PASS in 0.07s]
03:52:16  40 of 76 START sql view model `analytics`.`stg_customers` ...................... [RUN]
03:52:16  40 of 76 OK created sql view model `analytics`.`stg_customers` ................. [OK in 0.14s]
03:52:16  41 of 76 START sql view model `analytics`.`stg_orders` ......................... [RUN]
03:52:16  41 of 76 OK created sql view model `analytics`.`stg_orders` .................... [OK in 0.04s]
03:52:16  42 of 76 START sql view model `analytics`.`stg_payments` ....................... [RUN]
03:52:16  42 of 76 OK created sql view model `analytics`.`stg_payments` .................. [OK in 0.03s]
03:52:16  43 of 76 START sql view model `analytics`.`stg_refunds` ........................ [RUN]
03:52:16  43 of 76 OK created sql view model `analytics`.`stg_refunds` ................... [OK in 0.04s]
03:52:16  44 of 76 START test not_null_stg_customers_customer_id ......................... [RUN]
03:52:16  44 of 76 PASS not_null_stg_customers_customer_id ............................... [PASS in 0.02s]
03:52:16  45 of 76 START test unique_stg_customers_customer_id ........................... [RUN]
03:52:16  45 of 76 PASS unique_stg_customers_customer_id ................................. [PASS in 0.03s]
03:52:16  46 of 76 START test not_null_stg_orders_order_id ............................... [RUN]
03:52:16  46 of 76 PASS not_null_stg_orders_order_id ..................................... [PASS in 0.02s]
03:52:16  47 of 76 START test unique_stg_orders_order_id ................................. [RUN]
03:52:16  47 of 76 PASS unique_stg_orders_order_id ....................................... [PASS in 0.05s]
03:52:16  48 of 76 START test not_null_stg_payments_payment_id ........................... [RUN]
03:52:16  48 of 76 PASS not_null_stg_payments_payment_id ................................. [PASS in 0.02s]
03:52:16  49 of 76 START test unique_stg_payments_payment_id ............................. [RUN]
03:52:16  49 of 76 PASS unique_stg_payments_payment_id ................................... [PASS in 0.04s]
03:52:16  50 of 76 START test not_null_stg_refunds_refund_id ............................. [RUN]
03:52:16  50 of 76 PASS not_null_stg_refunds_refund_id ................................... [PASS in 0.02s]
03:52:16  51 of 76 START test unique_stg_refunds_refund_id ............................... [RUN]
03:52:16  51 of 76 PASS unique_stg_refunds_refund_id ..................................... [PASS in 0.03s]
03:52:16  52 of 76 START sql table model `analytics`.`dim_customers` ..................... [RUN]
03:52:17  52 of 76 OK created sql table model `analytics`.`dim_customers` ................ [OK in 0.33s]
03:52:17  53 of 76 START sql view model `analytics`.`int_order_payments` ................. [RUN]
03:52:17  53 of 76 OK created sql view model `analytics`.`int_order_payments` ............ [OK in 0.04s]
03:52:17  54 of 76 START sql view model `analytics`.`int_order_refunds` .................. [RUN]
03:52:17  54 of 76 OK created sql view model `analytics`.`int_order_refunds` ............. [OK in 0.04s]
03:52:17  55 of 76 START test not_null_dim_customers_customer_id ......................... [RUN]
03:52:17  55 of 76 PASS not_null_dim_customers_customer_id ............................... [PASS in 0.02s]
03:52:17  56 of 76 START test unique_dim_customers_customer_id ........................... [RUN]
03:52:17  56 of 76 PASS unique_dim_customers_customer_id ................................. [PASS in 0.04s]
03:52:17  57 of 76 START test not_null_int_order_payments_order_id ....................... [RUN]
03:52:17  57 of 76 PASS not_null_int_order_payments_order_id ............................. [PASS in 0.04s]
03:52:17  58 of 76 START test not_null_int_order_payments_successful_payment_amount_cents  [RUN]
03:52:17  58 of 76 PASS not_null_int_order_payments_successful_payment_amount_cents ...... [PASS in 0.04s]
03:52:17  59 of 76 START test not_null_int_order_payments_successful_payment_count ....... [RUN]
03:52:17  59 of 76 PASS not_null_int_order_payments_successful_payment_count ............. [PASS in 0.04s]
03:52:17  60 of 76 START test unique_int_order_payments_order_id ......................... [RUN]
03:52:17  60 of 76 PASS unique_int_order_payments_order_id ............................... [PASS in 0.06s]
03:52:17  61 of 76 START test not_null_int_order_refunds_order_id ........................ [RUN]
03:52:17  61 of 76 PASS not_null_int_order_refunds_order_id .............................. [PASS in 0.04s]
03:52:17  62 of 76 START test not_null_int_order_refunds_successful_refund_amount_cents .. [RUN]
03:52:17  62 of 76 PASS not_null_int_order_refunds_successful_refund_amount_cents ........ [PASS in 0.04s]
03:52:17  63 of 76 START test not_null_int_order_refunds_successful_refund_count ......... [RUN]
03:52:17  63 of 76 PASS not_null_int_order_refunds_successful_refund_count ............... [PASS in 0.03s]
03:52:17  64 of 76 START test unique_int_order_refunds_order_id .......................... [RUN]
03:52:17  64 of 76 PASS unique_int_order_refunds_order_id ................................ [PASS in 0.03s]
03:52:17  65 of 76 START sql table model `analytics`.`fct_orders` ........................ [RUN]
03:52:18  65 of 76 OK created sql table model `analytics`.`fct_orders` ................... [OK in 0.22s]
03:52:18  66 of 76 START test accepted_values_fct_orders_order_status__completed__cancelled__refunded  [RUN]
03:52:18  66 of 76 PASS accepted_values_fct_orders_order_status__completed__cancelled__refunded  [PASS in 0.04s]
03:52:18  67 of 76 START test assert_cancelled_orders_are_unpaid ......................... [RUN]
03:52:18  67 of 76 PASS assert_cancelled_orders_are_unpaid ............................... [PASS in 0.04s]
03:52:18  68 of 76 START test assert_fct_orders_matches_source_count ..................... [RUN]
03:52:18  68 of 76 PASS assert_fct_orders_matches_source_count ........................... [PASS in 0.04s]
03:52:18  69 of 76 START test assert_refunds_do_not_exceed_payments ...................... [RUN]
03:52:18  69 of 76 PASS assert_refunds_do_not_exceed_payments ............................ [PASS in 0.04s]
03:52:18  70 of 76 START test assert_successful_payments_match_orders .................... [RUN]
03:52:18  70 of 76 PASS assert_successful_payments_match_orders .......................... [PASS in 0.04s]
03:52:18  71 of 76 START test not_null_fct_orders_customer_id ............................ [RUN]
03:52:18  71 of 76 PASS not_null_fct_orders_customer_id .................................. [PASS in 0.04s]
03:52:18  72 of 76 START test not_null_fct_orders_order_id ............................... [RUN]
03:52:18  72 of 76 PASS not_null_fct_orders_order_id ..................................... [PASS in 0.04s]
03:52:18  73 of 76 START test not_null_fct_orders_successful_payment_amount_cents ........ [RUN]
03:52:18  73 of 76 PASS not_null_fct_orders_successful_payment_amount_cents .............. [PASS in 0.04s]
03:52:18  74 of 76 START test not_null_fct_orders_successful_refund_amount_cents ......... [RUN]
03:52:18  74 of 76 PASS not_null_fct_orders_successful_refund_amount_cents ............... [PASS in 0.04s]
03:52:18  75 of 76 START test relationships_fct_orders_customer_id__customer_id__ref_dim_customers_  [RUN]
03:52:18  75 of 76 PASS relationships_fct_orders_customer_id__customer_id__ref_dim_customers_  [PASS in 0.05s]
03:52:18  76 of 76 START test unique_fct_orders_order_id ................................. [RUN]
03:52:18  76 of 76 PASS unique_fct_orders_order_id ....................................... [PASS in 0.06s]
03:52:18  
03:52:18  Finished running 2 table models, 68 data tests, 6 view models in 0 hours 0 minutes and 4.19 seconds (4.19s).
03:52:18  
03:52:18  Completed successfully
03:52:18  
03:52:18  Done. PASS=76 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=76
03:52:25  Running with dbt=1.11.14
03:52:25  Registered adapter: clickhouse=1.10.2
03:52:26  Found 8 models, 68 data tests, 7 sources, 536 macros
03:52:26  
03:52:26  Concurrency: 1 threads (target='dev')
03:52:26  
03:52:27  1 of 68 START test accepted_values_fct_orders_order_status__completed__cancelled__refunded  [RUN]
03:52:27  1 of 68 PASS accepted_values_fct_orders_order_status__completed__cancelled__refunded  [PASS in 0.19s]
03:52:27  2 of 68 START test assert_cancelled_orders_are_unpaid .......................... [RUN]
03:52:27  2 of 68 PASS assert_cancelled_orders_are_unpaid ................................ [PASS in 0.03s]
03:52:27  3 of 68 START test assert_fct_orders_matches_source_count ...................... [RUN]
03:52:27  3 of 68 PASS assert_fct_orders_matches_source_count ............................ [PASS in 0.03s]
03:52:27  4 of 68 START test assert_refunds_do_not_exceed_payments ....................... [RUN]
03:52:27  4 of 68 PASS assert_refunds_do_not_exceed_payments ............................. [PASS in 0.03s]
03:52:27  5 of 68 START test assert_successful_payments_match_orders ..................... [RUN]
03:52:27  5 of 68 PASS assert_successful_payments_match_orders ........................... [PASS in 0.04s]
03:52:27  6 of 68 START test not_null_dim_customers_customer_id .......................... [RUN]
03:52:27  6 of 68 PASS not_null_dim_customers_customer_id ................................ [PASS in 0.04s]
03:52:27  7 of 68 START test not_null_fct_orders_customer_id ............................. [RUN]
03:52:27  7 of 68 PASS not_null_fct_orders_customer_id ................................... [PASS in 0.05s]
03:52:27  8 of 68 START test not_null_fct_orders_order_id ................................ [RUN]
03:52:28  8 of 68 PASS not_null_fct_orders_order_id ...................................... [PASS in 0.07s]
03:52:28  9 of 68 START test not_null_fct_orders_successful_payment_amount_cents ......... [RUN]
03:52:28  9 of 68 PASS not_null_fct_orders_successful_payment_amount_cents ............... [PASS in 0.04s]
03:52:28  10 of 68 START test not_null_fct_orders_successful_refund_amount_cents ......... [RUN]
03:52:28  10 of 68 PASS not_null_fct_orders_successful_refund_amount_cents ............... [PASS in 0.06s]
03:52:28  11 of 68 START test not_null_int_order_payments_order_id ....................... [RUN]
03:52:28  11 of 68 PASS not_null_int_order_payments_order_id ............................. [PASS in 0.05s]
03:52:28  12 of 68 START test not_null_int_order_payments_successful_payment_amount_cents  [RUN]
03:52:28  12 of 68 PASS not_null_int_order_payments_successful_payment_amount_cents ...... [PASS in 0.11s]
03:52:28  13 of 68 START test not_null_int_order_payments_successful_payment_count ....... [RUN]
03:52:28  13 of 68 PASS not_null_int_order_payments_successful_payment_count ............. [PASS in 0.06s]
03:52:28  14 of 68 START test not_null_int_order_refunds_order_id ........................ [RUN]
03:52:28  14 of 68 PASS not_null_int_order_refunds_order_id .............................. [PASS in 0.03s]
03:52:28  15 of 68 START test not_null_int_order_refunds_successful_refund_amount_cents .. [RUN]
03:52:28  15 of 68 PASS not_null_int_order_refunds_successful_refund_amount_cents ........ [PASS in 0.04s]
03:52:28  16 of 68 START test not_null_int_order_refunds_successful_refund_count ......... [RUN]
03:52:28  16 of 68 PASS not_null_int_order_refunds_successful_refund_count ............... [PASS in 0.05s]
03:52:28  17 of 68 START test not_null_stg_customers_customer_id ......................... [RUN]
03:52:28  17 of 68 PASS not_null_stg_customers_customer_id ............................... [PASS in 0.04s]
03:52:28  18 of 68 START test not_null_stg_orders_order_id ............................... [RUN]
03:52:28  18 of 68 PASS not_null_stg_orders_order_id ..................................... [PASS in 0.04s]
03:52:28  19 of 68 START test not_null_stg_payments_payment_id ........................... [RUN]
03:52:28  19 of 68 PASS not_null_stg_payments_payment_id ................................. [PASS in 0.04s]
03:52:28  20 of 68 START test not_null_stg_refunds_refund_id ............................. [RUN]
03:52:28  20 of 68 PASS not_null_stg_refunds_refund_id ................................... [PASS in 0.04s]
03:52:28  21 of 68 START test relationships_fct_orders_customer_id__customer_id__ref_dim_customers_  [RUN]
03:52:28  21 of 68 PASS relationships_fct_orders_customer_id__customer_id__ref_dim_customers_  [PASS in 0.07s]
03:52:28  22 of 68 START test source_accepted_values_raw_customers_country__US__DE__GB__TR__BR  [RUN]
03:52:28  22 of 68 PASS source_accepted_values_raw_customers_country__US__DE__GB__TR__BR . [PASS in 0.06s]
03:52:28  23 of 68 START test source_accepted_values_raw_marketing_attribution_acquisition_channel__organic__paid_search__email__affiliate  [RUN]
03:52:28  23 of 68 PASS source_accepted_values_raw_marketing_attribution_acquisition_channel__organic__paid_search__email__affiliate  [PASS in 0.05s]
03:52:28  24 of 68 START test source_accepted_values_raw_orders_currency__USD__EUR__GBP__TRY  [RUN]
03:52:28  24 of 68 PASS source_accepted_values_raw_orders_currency__USD__EUR__GBP__TRY ... [PASS in 0.05s]
03:52:28  25 of 68 START test source_accepted_values_raw_orders_order_status__completed__cancelled__refunded  [RUN]
03:52:28  25 of 68 PASS source_accepted_values_raw_orders_order_status__completed__cancelled__refunded  [PASS in 0.04s]
03:52:28  26 of 68 START test source_accepted_values_raw_payments_payment_status__succeeded__voided  [RUN]
03:52:29  26 of 68 PASS source_accepted_values_raw_payments_payment_status__succeeded__voided  [PASS in 0.05s]
03:52:29  27 of 68 START test source_accepted_values_raw_refunds_refund_status__succeeded__failed  [RUN]
03:52:29  27 of 68 PASS source_accepted_values_raw_refunds_refund_status__succeeded__failed  [PASS in 0.05s]
03:52:29  28 of 68 START test source_accepted_values_raw_sessions_acquisition_channel__organic__paid_search__email__affiliate  [RUN]
03:52:29  28 of 68 PASS source_accepted_values_raw_sessions_acquisition_channel__organic__paid_search__email__affiliate  [PASS in 0.04s]
03:52:29  29 of 68 START test source_not_null_raw_customers_country ...................... [RUN]
03:52:29  29 of 68 PASS source_not_null_raw_customers_country ............................ [PASS in 0.03s]
03:52:29  30 of 68 START test source_not_null_raw_customers_customer_id .................. [RUN]
03:52:29  30 of 68 PASS source_not_null_raw_customers_customer_id ........................ [PASS in 0.06s]
03:52:29  31 of 68 START test source_not_null_raw_marketing_attribution_attribution_event_id  [RUN]
03:52:29  31 of 68 PASS source_not_null_raw_marketing_attribution_attribution_event_id ... [PASS in 0.04s]
03:52:29  32 of 68 START test source_not_null_raw_marketing_attribution_order_id ......... [RUN]
03:52:29  32 of 68 PASS source_not_null_raw_marketing_attribution_order_id ............... [PASS in 0.04s]
03:52:29  33 of 68 START test source_not_null_raw_marketing_attribution_session_id ....... [RUN]
03:52:29  33 of 68 PASS source_not_null_raw_marketing_attribution_session_id ............. [PASS in 0.03s]
03:52:29  34 of 68 START test source_not_null_raw_order_items_order_id ................... [RUN]
03:52:29  34 of 68 PASS source_not_null_raw_order_items_order_id ......................... [PASS in 0.03s]
03:52:29  35 of 68 START test source_not_null_raw_order_items_order_item_id .............. [RUN]
03:52:29  35 of 68 PASS source_not_null_raw_order_items_order_item_id .................... [PASS in 0.03s]
03:52:29  36 of 68 START test source_not_null_raw_orders_currency ........................ [RUN]
03:52:29  36 of 68 PASS source_not_null_raw_orders_currency .............................. [PASS in 0.03s]
03:52:29  37 of 68 START test source_not_null_raw_orders_customer_id ..................... [RUN]
03:52:29  37 of 68 PASS source_not_null_raw_orders_customer_id ........................... [PASS in 0.04s]
03:52:29  38 of 68 START test source_not_null_raw_orders_order_id ........................ [RUN]
03:52:29  38 of 68 PASS source_not_null_raw_orders_order_id .............................. [PASS in 0.03s]
03:52:29  39 of 68 START test source_not_null_raw_orders_order_status .................... [RUN]
03:52:29  39 of 68 PASS source_not_null_raw_orders_order_status .......................... [PASS in 0.03s]
03:52:29  40 of 68 START test source_not_null_raw_payments_order_id ...................... [RUN]
03:52:29  40 of 68 PASS source_not_null_raw_payments_order_id ............................ [PASS in 0.03s]
03:52:29  41 of 68 START test source_not_null_raw_payments_payment_id .................... [RUN]
03:52:29  41 of 68 PASS source_not_null_raw_payments_payment_id .......................... [PASS in 0.03s]
03:52:29  42 of 68 START test source_not_null_raw_payments_payment_status ................ [RUN]
03:52:29  42 of 68 PASS source_not_null_raw_payments_payment_status ...................... [PASS in 0.03s]
03:52:29  43 of 68 START test source_not_null_raw_refunds_order_id ....................... [RUN]
03:52:29  43 of 68 PASS source_not_null_raw_refunds_order_id ............................. [PASS in 0.03s]
03:52:29  44 of 68 START test source_not_null_raw_refunds_refund_id ...................... [RUN]
03:52:29  44 of 68 PASS source_not_null_raw_refunds_refund_id ............................ [PASS in 0.03s]
03:52:29  45 of 68 START test source_not_null_raw_refunds_refund_status .................. [RUN]
03:52:29  45 of 68 PASS source_not_null_raw_refunds_refund_status ........................ [PASS in 0.03s]
03:52:29  46 of 68 START test source_not_null_raw_sessions_customer_id ................... [RUN]
03:52:29  46 of 68 PASS source_not_null_raw_sessions_customer_id ......................... [PASS in 0.03s]
03:52:29  47 of 68 START test source_not_null_raw_sessions_session_id .................... [RUN]
03:52:29  47 of 68 PASS source_not_null_raw_sessions_session_id .......................... [PASS in 0.03s]
03:52:29  48 of 68 START test source_relationships_raw_marketing_attribution_order_id__order_id__source_raw_orders_  [RUN]
03:52:29  48 of 68 PASS source_relationships_raw_marketing_attribution_order_id__order_id__source_raw_orders_  [PASS in 0.08s]
03:52:29  49 of 68 START test source_relationships_raw_marketing_attribution_session_id__session_id__source_raw_sessions_  [RUN]
03:52:30  49 of 68 PASS source_relationships_raw_marketing_attribution_session_id__session_id__source_raw_sessions_  [PASS in 0.08s]
03:52:30  50 of 68 START test source_relationships_raw_order_items_order_id__order_id__source_raw_orders_  [RUN]
03:52:30  50 of 68 PASS source_relationships_raw_order_items_order_id__order_id__source_raw_orders_  [PASS in 0.07s]
03:52:30  51 of 68 START test source_relationships_raw_orders_customer_id__customer_id__source_raw_customers_  [RUN]
03:52:30  51 of 68 PASS source_relationships_raw_orders_customer_id__customer_id__source_raw_customers_  [PASS in 0.06s]
03:52:30  52 of 68 START test source_relationships_raw_payments_order_id__order_id__source_raw_orders_  [RUN]
03:52:30  52 of 68 PASS source_relationships_raw_payments_order_id__order_id__source_raw_orders_  [PASS in 0.04s]
03:52:30  53 of 68 START test source_relationships_raw_refunds_order_id__order_id__source_raw_orders_  [RUN]
03:52:30  53 of 68 PASS source_relationships_raw_refunds_order_id__order_id__source_raw_orders_  [PASS in 0.05s]
03:52:30  54 of 68 START test source_relationships_raw_sessions_customer_id__customer_id__source_raw_customers_  [RUN]
03:52:30  54 of 68 PASS source_relationships_raw_sessions_customer_id__customer_id__source_raw_customers_  [PASS in 0.04s]
03:52:30  55 of 68 START test source_unique_raw_customers_customer_id .................... [RUN]
03:52:30  55 of 68 PASS source_unique_raw_customers_customer_id .......................... [PASS in 0.03s]
03:52:30  56 of 68 START test source_unique_raw_order_items_order_item_id ................ [RUN]
03:52:30  56 of 68 PASS source_unique_raw_order_items_order_item_id ...................... [PASS in 0.07s]
03:52:30  57 of 68 START test source_unique_raw_orders_order_id .......................... [RUN]
03:52:30  57 of 68 PASS source_unique_raw_orders_order_id ................................ [PASS in 0.06s]
03:52:30  58 of 68 START test source_unique_raw_payments_payment_id ...................... [RUN]
03:52:30  58 of 68 PASS source_unique_raw_payments_payment_id ............................ [PASS in 0.05s]
03:52:30  59 of 68 START test source_unique_raw_refunds_refund_id ........................ [RUN]
03:52:30  59 of 68 PASS source_unique_raw_refunds_refund_id .............................. [PASS in 0.03s]
03:52:30  60 of 68 START test source_unique_raw_sessions_session_id ...................... [RUN]
03:52:30  60 of 68 PASS source_unique_raw_sessions_session_id ............................ [PASS in 0.05s]
03:52:30  61 of 68 START test unique_dim_customers_customer_id ........................... [RUN]
03:52:30  61 of 68 PASS unique_dim_customers_customer_id ................................. [PASS in 0.13s]
03:52:30  62 of 68 START test unique_fct_orders_order_id ................................. [RUN]
03:52:30  62 of 68 PASS unique_fct_orders_order_id ....................................... [PASS in 0.07s]
03:52:30  63 of 68 START test unique_int_order_payments_order_id ......................... [RUN]
03:52:30  63 of 68 PASS unique_int_order_payments_order_id ............................... [PASS in 0.06s]
03:52:30  64 of 68 START test unique_int_order_refunds_order_id .......................... [RUN]
03:52:30  64 of 68 PASS unique_int_order_refunds_order_id ................................ [PASS in 0.05s]
03:52:30  65 of 68 START test unique_stg_customers_customer_id ........................... [RUN]
03:52:31  65 of 68 PASS unique_stg_customers_customer_id ................................. [PASS in 0.04s]
03:52:31  66 of 68 START test unique_stg_orders_order_id ................................. [RUN]
03:52:31  66 of 68 PASS unique_stg_orders_order_id ....................................... [PASS in 0.06s]
03:52:31  67 of 68 START test unique_stg_payments_payment_id ............................. [RUN]
03:52:31  67 of 68 PASS unique_stg_payments_payment_id ................................... [PASS in 0.04s]
03:52:31  68 of 68 START test unique_stg_refunds_refund_id ............................... [RUN]
03:52:31  68 of 68 PASS unique_stg_refunds_refund_id ..................................... [PASS in 0.03s]
03:52:31  
03:52:31  Finished running 68 data tests in 0 hours 0 minutes and 4.24 seconds (4.24s).
03:52:31  
03:52:31  Completed successfully
03:52:31  
03:52:31  Done. PASS=68 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=68
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
