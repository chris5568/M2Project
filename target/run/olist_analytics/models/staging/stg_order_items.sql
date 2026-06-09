

  create or replace view `assignment-project-498814`.`analytics`.`stg_order_items`
  OPTIONS()
  as with raw_items as (
    select * from `assignment-project-498814`.`raw_olist`.`olist_order_items_dataset`
)
select
    cast(order_id as string) as order_id,
    cast(order_item_id as int64) as item_sequence,
    cast(product_id as string) as product_id,
    cast(seller_id as string) as seller_id,
    cast(price as float64) as price,
    cast(freight_value as float64) as freight_value
from raw_items
where order_id is not null;

