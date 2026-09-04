-- Fail fast if the baseline shape or required edge cases drift.

SELECT throwIf(
    (SELECT count() FROM system.tables WHERE database = 'raw') != 7,
    'Expected seven raw tables'
);

SELECT throwIf((SELECT count() FROM raw.customers) != 20000, 'customers count drift');
SELECT throwIf((SELECT count() FROM raw.orders) != 100000, 'orders count drift');
SELECT throwIf((SELECT count() FROM raw.order_items) != 300000, 'order_items count drift');
SELECT throwIf((SELECT count() FROM raw.payments) != 105000, 'payments count drift');
SELECT throwIf((SELECT count() FROM raw.refunds) != 10000, 'refunds count drift');
SELECT throwIf((SELECT count() FROM raw.sessions) != 120000, 'sessions count drift');
SELECT throwIf(
    (SELECT count() FROM raw.marketing_attribution) != 100100,
    'marketing_attribution count drift'
);

SELECT throwIf(
    (SELECT count() FROM raw.orders WHERE order_status = 'cancelled') = 0,
    'Missing cancelled orders'
);
SELECT throwIf(
    (SELECT uniqExact(currency) FROM raw.orders) < 4,
    'Missing multiple currencies'
);
SELECT throwIf(
    (SELECT count() FROM
        (SELECT order_id FROM raw.payments GROUP BY order_id HAVING count() > 1)) != 5000,
    'Split-payment edge case drift'
);
SELECT throwIf(
    (SELECT count() FROM
        (SELECT order_id FROM raw.refunds GROUP BY order_id HAVING count() > 1)) != 1000,
    'Multiple-refund edge case drift'
);
SELECT throwIf(
    (SELECT count() FROM raw.refunds AS refunds
        INNER JOIN raw.orders AS orders USING (order_id)
        WHERE refunds.amount_cents < orders.order_total_cents
          AND refunds.refund_status = 'succeeded') = 0,
    'Missing partial refunds'
);
SELECT throwIf(
    (SELECT count() FROM raw.refunds AS refunds
        INNER JOIN raw.orders AS orders USING (order_id)
        WHERE dateDiff('day', orders.ordered_at, refunds.refunded_at) > 30) = 0,
    'Missing late refunds'
);
SELECT throwIf(
    (SELECT count() FROM raw.sessions WHERE acquisition_channel IS NULL) = 0,
    'Missing NULL acquisition channels'
);
SELECT throwIf(
    (SELECT count() FROM raw.marketing_attribution)
        = (SELECT uniqExact(attribution_event_id) FROM raw.marketing_attribution),
    'Missing duplicate attribution events'
);

SELECT 'clickhouse baseline: PASS' AS result;

