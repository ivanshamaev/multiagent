-- Public, implementation-independent invariants. Exact expected rows remain in the hidden grader.

SELECT throwIf(
    (SELECT count() FROM system.tables
        WHERE database = 'analytics'
          AND name = 'fct_net_revenue'
          AND engine = 'MergeTree') != 1,
    'analytics.fct_net_revenue must be a physical MergeTree table'
);

SELECT throwIf(
    (SELECT count() FROM system.columns
        WHERE database = 'analytics'
          AND table = 'fct_net_revenue'
          AND name IN (
              'order_date', 'country', 'acquisition_channel', 'currency',
              'gross_payment_amount_cents', 'successful_refund_amount_cents',
              'net_revenue_cents'
          )) != 7,
    'fct_net_revenue is missing required columns'
);

SELECT throwIf(
    (SELECT count() FROM system.columns
        WHERE database = 'analytics'
          AND table = 'fct_net_revenue'
          AND startsWith(type, 'Nullable(')) != 0,
    'fct_net_revenue columns must be non-Nullable'
);

SELECT throwIf(
    (SELECT count() FROM analytics.fct_net_revenue)
        != (SELECT uniqExact(tuple(
            order_date, country, acquisition_channel, currency
        )) FROM analytics.fct_net_revenue),
    'fct_net_revenue declared grain is not unique'
);

SELECT throwIf(
    (SELECT countIf(
        net_revenue_cents != gross_payment_amount_cents - successful_refund_amount_cents
    ) FROM analytics.fct_net_revenue) != 0,
    'fct_net_revenue metric identity failed'
);

SELECT throwIf(
    (SELECT count() FROM system.columns
        WHERE database = 'analytics'
          AND table = 'fct_net_revenue'
          AND name = 'net_revenue_cents'
          AND startsWith(type, 'Int')) != 1,
    'net_revenue_cents must use a signed integer type'
);

SELECT 'net revenue public contract: PASS' AS result;
