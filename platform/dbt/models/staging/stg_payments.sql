select
    payment_id as payment_id,
    order_id as order_id,
    paid_at as paid_at,
    amount_cents as amount_cents,
    upper(currency) as currency,
    lower(payment_status) as payment_status
from {{ source('raw', 'payments') }}
