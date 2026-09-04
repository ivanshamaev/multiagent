select order_id
from {{ ref('fct_orders') }}
where order_status != 'cancelled'
  and successful_payment_amount_cents != order_total_cents

