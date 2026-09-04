select
    order_id as order_id,
    count() as successful_payment_count,
    sum(amount_cents) as successful_payment_amount_cents,
    min(paid_at) as first_successful_payment_at,
    max(paid_at) as last_successful_payment_at
from {{ ref('stg_payments') }}
where payment_status = 'succeeded'
group by order_id
