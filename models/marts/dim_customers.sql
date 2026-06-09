with raw_customers as (
    select * from {{ source('raw_olist', 'olist_customers_dataset') }}
),
sales as (
    select * from {{ ref('fact_sales') }}
),
customer_spend as (
    select
        customer_id,
        sum(total_sale_amount) as lifetime_spend,
        count(distinct order_id) as total_orders
    from sales
    group by 1
)
select
    cast(c.customer_id as string) as customer_key,
    cast(c.customer_unique_id as string) as customer_unique_id,
    c.customer_city as city,
    c.customer_state as state,
    coalesce(s.lifetime_spend, 0.0) as lifetime_spend,
    coalesce(s.total_orders, 0) as total_orders
from raw_customers c
left join customer_spend s on c.customer_id = s.customer_id
