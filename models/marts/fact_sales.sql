with orders as (
    select * from {{ ref('stg_orders') }}
),
items as (
    select * from {{ ref('stg_order_items') }}
),
payments as (
    select order_id, sum(cast(payment_value as float64)) as total_payment_received
    from {{ ref('stg_order_payments') }}
    group by 1
),
reviews as (
    select order_id, avg(cast(review_score as float64)) as avg_review_score
    from {{ ref('stg_order_reviews') }}
    group by 1
)
select
    md5(concat(coalesce(items.order_id, ''), '-', coalesce(cast(items.item_sequence as string), ''))) as sales_key,
    items.order_id,
    orders.customer_id,
    items.product_id as product_key,
    items.seller_id as seller_key,
    orders.purchase_at,
    orders.order_status,
    items.price,
    items.freight_value,
    (items.price + items.freight_value) as total_sale_amount,
    coalesce(p.total_payment_received, 0.0) as order_payment_total,
    coalesce(r.avg_review_score, 0.0) as review_score
from items
join orders on items.order_id = orders.order_id
left join payments p on items.order_id = p.order_id
left join reviews r on items.order_id = r.order_id
where orders.order_status = 'delivered'
