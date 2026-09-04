-- Deterministic local-only ecommerce dataset.
-- Net Revenue is intentionally absent: it is a future agent task.

DROP DATABASE IF EXISTS raw SYNC;
CREATE DATABASE raw;

CREATE TABLE raw.customers
(
    customer_id UInt64,
    country LowCardinality(String),
    created_at DateTime64(3, 'UTC'),
    updated_at DateTime64(3, 'UTC')
)
ENGINE = MergeTree
ORDER BY customer_id;

INSERT INTO raw.customers
SELECT
    number + 1 AS customer_id,
    arrayElement(['US', 'DE', 'GB', 'TR', 'BR'], (number % 5) + 1) AS country,
    toDateTime64('2024-01-01 00:00:00', 3, 'UTC')
        + toIntervalMinute(number % 525600) AS created_at,
    created_at + toIntervalDay(number % 30) AS updated_at
FROM numbers(20000);

CREATE TABLE raw.orders
(
    order_id UInt64,
    customer_id UInt64,
    order_status LowCardinality(String),
    ordered_at DateTime64(3, 'UTC'),
    currency LowCardinality(String),
    order_total_cents UInt64,
    updated_at DateTime64(3, 'UTC')
)
ENGINE = MergeTree
ORDER BY order_id;

INSERT INTO raw.orders
SELECT
    number + 1 AS order_id,
    (number % 20000) + 1 AS customer_id,
    multiIf(
        order_id % 20 = 0, 'cancelled',
        order_id % 13 = 0, 'refunded',
        'completed'
    ) AS order_status,
    toDateTime64('2025-01-01 00:00:00', 3, 'UTC')
        + toIntervalSecond(number % 31536000) AS ordered_at,
    arrayElement(['USD', 'EUR', 'GBP', 'TRY'], (number % 4) + 1) AS currency,
    1000 + (number % 40000) AS order_total_cents,
    ordered_at + toIntervalMinute(number % 180) AS updated_at
FROM numbers(100000);

CREATE TABLE raw.order_items
(
    order_item_id UInt64,
    order_id UInt64,
    product_id UInt64,
    quantity UInt8,
    unit_price_cents UInt32
)
ENGINE = MergeTree
ORDER BY (order_id, order_item_id);

INSERT INTO raw.order_items
SELECT
    number + 1 AS order_item_id,
    intDiv(number, 3) + 1 AS order_id,
    (number % 5000) + 1 AS product_id,
    CAST((number % 3) + 1, 'UInt8') AS quantity,
    CAST(300 + (number % 12000), 'UInt32') AS unit_price_cents
FROM numbers(300000);

CREATE TABLE raw.payments
(
    payment_id UInt64,
    order_id UInt64,
    paid_at DateTime64(3, 'UTC'),
    amount_cents UInt64,
    currency LowCardinality(String),
    payment_status LowCardinality(String)
)
ENGINE = MergeTree
ORDER BY (order_id, payment_id);

-- The first payment is half-sized for every tenth non-cancelled order.
INSERT INTO raw.payments
SELECT
    order_id AS payment_id,
    order_id,
    ordered_at + toIntervalMinute(5) AS paid_at,
    if(order_id % 10 = 0 AND order_status != 'cancelled',
        intDiv(order_total_cents, 2), order_total_cents) AS amount_cents,
    currency,
    if(order_status = 'cancelled', 'voided', 'succeeded') AS payment_status
FROM raw.orders;

-- A second payment completes 5,000 split-payment orders.
INSERT INTO raw.payments
SELECT
    100000 + intDiv(order_id, 10) AS payment_id,
    order_id,
    ordered_at + toIntervalMinute(7) AS paid_at,
    order_total_cents - intDiv(order_total_cents, 2) AS amount_cents,
    currency,
    'succeeded' AS payment_status
FROM raw.orders
WHERE order_id % 10 = 0 AND order_status != 'cancelled';

CREATE TABLE raw.refunds
(
    refund_id UInt64,
    order_id UInt64,
    refunded_at DateTime64(3, 'UTC'),
    amount_cents UInt64,
    refund_status LowCardinality(String)
)
ENGINE = MergeTree
ORDER BY (order_id, refund_id);

-- 8,000 single-refund orders plus 1,000 orders with two refunds each.
INSERT INTO raw.refunds
WITH
    if(number < 8000,
        (number * toUInt64(10)) + toUInt64(2),
        toUInt64(
            toInt64(80002) + (intDiv(toInt64(number) - 8000, 2) * 10)
        ))
        AS selected_order_id
SELECT
    number + 1 AS refund_id,
    selected_order_id AS order_id,
    orders.ordered_at
        + toIntervalDay(if(number % 19 = 0, 45, (number % 25) + 1)) AS refunded_at,
    if(number >= 8000,
        intDiv(orders.order_total_cents, 10),
        if(number % 5 = 0,
            orders.order_total_cents,
            intDiv(orders.order_total_cents, 4))) AS amount_cents,
    if(number % 23 = 0, 'failed', 'succeeded') AS refund_status
FROM numbers(10000) AS generated
INNER JOIN raw.orders AS orders ON orders.order_id = selected_order_id;

CREATE TABLE raw.sessions
(
    session_id UInt64,
    customer_id UInt64,
    occurred_at DateTime64(3, 'UTC'),
    acquisition_channel Nullable(String)
)
ENGINE = MergeTree
ORDER BY session_id;

INSERT INTO raw.sessions
SELECT
    number + 1 AS session_id,
    (number % 20000) + 1 AS customer_id,
    toDateTime64('2024-12-15 23:30:00', 3, 'UTC')
        + toIntervalSecond(number % 15552000) AS occurred_at,
    nullIf(
        arrayElement(['', 'organic', 'paid_search', 'email', 'affiliate'], (number % 5) + 1),
        ''
    ) AS acquisition_channel
FROM numbers(120000);

CREATE TABLE raw.marketing_attribution
(
    attribution_event_id UInt64,
    order_id UInt64,
    session_id UInt64,
    acquisition_channel Nullable(String),
    attributed_at DateTime64(3, 'UTC')
)
ENGINE = MergeTree
ORDER BY (attribution_event_id, order_id);

-- The final 100 rows exactly duplicate earlier events.
INSERT INTO raw.marketing_attribution
WITH
    if(
        number < 100000,
        number + toUInt64(1),
        toUInt64(toInt64(number) - 99999)
    ) AS source_number
SELECT
    source_number AS attribution_event_id,
    source_number AS order_id,
    source_number AS session_id,
    nullIf(
        arrayElement(
            ['', 'organic', 'paid_search', 'email', 'affiliate'],
            ((source_number - 1) % 5) + 1
        ),
        ''
    ) AS acquisition_channel,
    toDateTime64('2025-01-01 00:00:00', 3, 'UTC')
        + toIntervalSecond((source_number - 1) % 31536000) AS attributed_at
FROM numbers(100100);
