-- Validate physical dbt objects and deterministic aggregates independently of dbt.

SELECT throwIf(
    (SELECT count() FROM system.tables
        WHERE database = 'analytics'
          AND name IN (
              'stg_customers', 'stg_orders', 'stg_payments', 'stg_refunds',
              'int_order_payments', 'int_order_refunds',
              'dim_customers', 'fct_orders'
          )) != 8,
    'Expected eight analytics relations'
);

SELECT throwIf(
    (SELECT count() FROM system.tables
        WHERE database = 'analytics'
          AND engine = 'View') != 6,
    'Expected six analytics views'
);
SELECT throwIf(
    (SELECT count() FROM system.tables
        WHERE database = 'analytics'
          AND engine = 'MergeTree') != 2,
    'Expected two MergeTree marts'
);
SELECT throwIf(
    (SELECT count() FROM system.tables
        WHERE database = 'analytics'
          AND startsWith(name, '__dbt_')) != 0,
    'Found leaked dbt temporary relations'
);
SELECT throwIf(
    (SELECT count() FROM system.tables
        WHERE database = 'analytics'
          AND positionCaseInsensitive(name, 'net_revenue') > 0) != 0,
    'Net Revenue must remain unsolved in the baseline'
);
SELECT throwIf(
    (SELECT count() FROM system.columns
        WHERE database = 'analytics'
          AND positionCaseInsensitive(name, 'net_revenue') > 0) != 0,
    'Net Revenue columns must remain absent from the baseline'
);

SELECT throwIf((SELECT count() FROM analytics.int_order_payments) != 95000,
    'successful payment aggregate count drift');
SELECT throwIf((SELECT count() FROM analytics.int_order_refunds) != 8652,
    'successful refund aggregate count drift');
SELECT throwIf((SELECT count() FROM analytics.dim_customers) != 20000,
    'customer dimension count drift');
SELECT throwIf((SELECT count() FROM analytics.fct_orders) != 100000,
    'order fact count drift');
SELECT throwIf(
    (SELECT sum(successful_payment_amount_cents) FROM analytics.fct_orders)
        != 1804905000,
    'successful payment amount drift'
);
SELECT throwIf(
    (SELECT sum(successful_refund_count) FROM analytics.fct_orders) != 9565,
    'successful refund event count drift'
);
SELECT throwIf(
    (SELECT sum(successful_refund_amount_cents) FROM analytics.fct_orders)
        != 65402953,
    'successful refund amount drift'
);

SELECT 'dbt baseline: PASS' AS result;
