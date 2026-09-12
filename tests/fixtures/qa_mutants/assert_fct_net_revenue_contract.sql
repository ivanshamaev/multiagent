-- qa-contract-test-v1
with row_violations as (
    select 1 as violation
    from {{ ref('fct_net_revenue') }}
    where
        order_date is null
        or country is null
        or acquisition_channel is null
        or currency is null
        or gross_payment_amount_cents is null
        or successful_refund_amount_cents is null
        or net_revenue_cents is null
        or net_revenue_cents != gross_payment_amount_cents - successful_refund_amount_cents
),
grain_violations as (
    select 1 as violation
    from {{ ref('fct_net_revenue') }}
    group by order_date, country, acquisition_channel, currency
    having count() > 1
)
select * from row_violations
union all
select * from grain_violations
