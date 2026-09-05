-- Logical checksums for reset reproducibility. Values are not task grading expectations.

SELECT object, rows, checksum
FROM
(
    SELECT
        'raw.customers' AS object,
        count() AS rows,
        toString(sum(toUInt128(cityHash64(
            customer_id, country, toUnixTimestamp64Milli(created_at),
            toUnixTimestamp64Milli(updated_at)
        )))) AS checksum
    FROM raw.customers

    UNION ALL

    SELECT
        'raw.orders',
        count(),
        toString(sum(toUInt128(cityHash64(
            order_id, customer_id, order_status, toUnixTimestamp64Milli(ordered_at),
            currency, order_total_cents, toUnixTimestamp64Milli(updated_at)
        ))))
    FROM raw.orders

    UNION ALL

    SELECT
        'raw.order_items',
        count(),
        toString(sum(toUInt128(cityHash64(
            order_item_id, order_id, product_id, quantity, unit_price_cents
        ))))
    FROM raw.order_items

    UNION ALL

    SELECT
        'raw.payments',
        count(),
        toString(sum(toUInt128(cityHash64(
            payment_id, order_id, toUnixTimestamp64Milli(paid_at), amount_cents,
            currency, payment_status
        ))))
    FROM raw.payments

    UNION ALL

    SELECT
        'raw.refunds',
        count(),
        toString(sum(toUInt128(cityHash64(
            refund_id, order_id, toUnixTimestamp64Milli(refunded_at), amount_cents, refund_status
        ))))
    FROM raw.refunds

    UNION ALL

    SELECT
        'raw.sessions',
        count(),
        toString(sum(toUInt128(cityHash64(
            session_id, customer_id, toUnixTimestamp64Milli(occurred_at),
            ifNull(acquisition_channel, '<NULL>')
        ))))
    FROM raw.sessions

    UNION ALL

    SELECT
        'raw.marketing_attribution',
        count(),
        toString(sum(toUInt128(cityHash64(
            attribution_event_id, order_id, session_id,
            ifNull(acquisition_channel, '<NULL>'), toUnixTimestamp64Milli(attributed_at)
        ))))
    FROM raw.marketing_attribution

    UNION ALL

    SELECT
        'analytics.baseline',
        count(),
        toString(sum(toUInt128(cityHash64(
            order_id, customer_id, country, order_status, toUnixTimestamp64Milli(ordered_at),
            toString(order_date), currency, order_total_cents, successful_payment_count,
            successful_payment_amount_cents, successful_refund_count,
            successful_refund_amount_cents
        ))))
    FROM analytics.fct_orders
)
ORDER BY object
FORMAT TabSeparatedRaw;
