

  create or replace view `assignment-project-498814`.`analytics`.`stg_order_payments`
  OPTIONS()
  as with raw_payments as (
    select * from `assignment-project-498814`.`raw_olist`.`olist_order_payments_dataset`
)
select
    cast(order_id as string) as order_id,
    cast(payment_sequential as int64) as payment_sequential,
    cast(payment_type as string) as payment_type,
    cast(payment_installments as int64) as payment_installments,
    cast(payment_value as float64) as payment_value
from raw_payments
where order_id is not null;

