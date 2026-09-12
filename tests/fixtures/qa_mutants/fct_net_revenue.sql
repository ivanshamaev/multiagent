{{ config(materialized='table', order_by=['order_date', 'country', 'acquisition_channel', 'currency']) }}

with deduplicated_attribution as (
    select
        attribution_event_id,
        argMax(order_id, tuple(attributed_at, attribution_event_id)) as attributed_order_id,
        argMax(
            ifNull(acquisition_channel, 'unknown'),
            tuple(attributed_at, attribution_event_id)
        ) as attributed_channel,
        max(attributed_at) as latest_attributed_at
    from {{ source('raw', 'marketing_attribution') }}
    group by attribution_event_id
),
attribution_by_order as (
    select
        attributed_order_id as order_id,
        argMax(
            ifNull(attributed_channel, 'unknown'),
            tuple(latest_attributed_at, attribution_event_id)
        ) as acquisition_channel
    from deduplicated_attribution
    group by attributed_order_id
),
components as (
    select
        orders.order_date as order_date,
        orders.country as country,
        ifNull(attribution.acquisition_channel, 'unknown') as acquisition_channel,
        orders.currency as currency,
        sum(toInt64(orders.successful_payment_amount_cents)) as gross_component,
        sum(toInt64(orders.successful_refund_amount_cents)) as refund_component
    from {{ ref('fct_orders') }} as orders
    left join attribution_by_order as attribution using (order_id)
    group by order_date, country, acquisition_channel, currency
)
select
    order_date,
    country,
    acquisition_channel,
    currency,
    gross_component as gross_payment_amount_cents,
    refund_component as successful_refund_amount_cents,
    gross_component - refund_component as net_revenue_cents
from components
