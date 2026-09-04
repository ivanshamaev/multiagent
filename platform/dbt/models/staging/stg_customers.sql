select
    customer_id as customer_id,
    country as country,
    created_at as created_at,
    updated_at as updated_at
from {{ source('raw', 'customers') }}
