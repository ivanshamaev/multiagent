{{ config(order_by=['order_date', 'order_id']) }}

select
    orders.order_id as order_id,
    orders.customer_id as customer_id,
    customers.country as country,
    orders.order_status as order_status,
    orders.ordered_at as ordered_at,
    toDate(orders.ordered_at, 'UTC') as order_date,
    orders.currency as currency,
    orders.order_total_cents as order_total_cents,
    ifNull(payments.successful_payment_count, toUInt64(0)) as successful_payment_count,
    ifNull(
        payments.successful_payment_amount_cents,
        toUInt64(0)
    ) as successful_payment_amount_cents,
    ifNull(refunds.successful_refund_count, toUInt64(0)) as successful_refund_count,
    ifNull(
        refunds.successful_refund_amount_cents,
        toUInt64(0)
    ) as successful_refund_amount_cents,
    payments.first_successful_payment_at as first_successful_payment_at,
    payments.last_successful_payment_at as last_successful_payment_at,
    refunds.first_successful_refund_at as first_successful_refund_at,
    refunds.last_successful_refund_at as last_successful_refund_at
from {{ ref('stg_orders') }} as orders
inner join {{ ref('dim_customers') }} as customers using (customer_id)
left join {{ ref('int_order_payments') }} as payments using (order_id)
left join {{ ref('int_order_refunds') }} as refunds using (order_id)
