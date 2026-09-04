select
    (select count() from {{ ref('fct_orders') }}) as fact_count,
    (select count() from {{ source('raw', 'orders') }}) as source_count
where fact_count != source_count
