select order_id
from {{ ref('fct_orders') }}
where successful_refund_amount_cents > successful_payment_amount_cents
