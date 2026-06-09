with raw_orders as (
    select * from {{ source('raw_olist', 'olist_orders_dataset') }}
)
select
    cast(order_id as string) as order_id,
    cast(customer_id as string) as customer_id,
    cast(order_status as string) as order_status,
    safe_cast(order_purchase_timestamp as timestamp) as purchase_at,
    safe_cast(order_approved_at as timestamp) as approved_at,
    safe_cast(order_delivered_customer_date as timestamp) as delivered_at
from raw_orders
where order_id is not null
