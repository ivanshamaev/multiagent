select
    order_id as order_id,
    count() as successful_refund_count,
    sum(amount_cents) as successful_refund_amount_cents,
    min(refunded_at) as first_successful_refund_at,
    max(refunded_at) as last_successful_refund_at
from {{ ref('stg_refunds') }}
where refund_status = 'succeeded'
group by order_id
