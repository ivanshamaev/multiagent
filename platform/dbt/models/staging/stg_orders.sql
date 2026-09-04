select
    order_id as order_id,
    customer_id as customer_id,
    lower(order_status) as order_status,
    ordered_at as ordered_at,
    upper(currency) as currency,
    order_total_cents as order_total_cents,
    updated_at as updated_at
from {{ source('raw', 'orders') }}
