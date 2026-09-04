select
    refund_id as refund_id,
    order_id as order_id,
    refunded_at as refunded_at,
    amount_cents as amount_cents,
    lower(refund_status) as refund_status
from {{ source('raw', 'refunds') }}
