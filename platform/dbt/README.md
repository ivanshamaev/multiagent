# dbt baseline

Этот dbt project выполняется только одноразовым контейнером из Compose. Host-установка dbt не требуется. Образ фиксирует Python 3.12.14, dbt Core 1.11.14 и dbt-clickhouse 1.10.2; полный dependency graph хранится в `requirements.lock`.

## Слои

- `staging/` — четыре view без фильтрации строк из `raw`.
- `intermediate/` — успешные payment/refund events, агрегированные до одной строки на order.
- `marts/` — `dim_customers` и `fct_orders` как MergeTree tables.

Baseline намеренно хранит payment и refund отдельно. Он не вычисляет Net Revenue и не подготавливает attribution — это остаётся проверяемой задачей будущего Data Engineer Agent.

## Проверка

```bash
make platform-up
make seed
make dbt-debug
make dbt-parse
make dbt-compile
make dbt-build
make platform-test
```

`make seed` пересоздаёт `raw` и очищает производную базу `analytics`. `make dbt-build` можно безопасно повторять без reset; `make platform-test` объединяет raw smoke, dbt tests и независимые SQL-инварианты физических объектов.
