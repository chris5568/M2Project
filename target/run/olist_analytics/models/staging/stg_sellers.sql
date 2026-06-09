

  create or replace view `assignment-project-498814`.`analytics`.`stg_sellers`
  OPTIONS()
  as with raw_sellers as (
    select * from `assignment-project-498814`.`raw_olist`.`olist_sellers_dataset`
)
select
    cast(seller_id as string) as seller_id,
    cast(seller_zip_code_prefix as int64) as seller_zip_code_prefix,
    cast(seller_city as string) as seller_city,
    cast(seller_state as string) as seller_state
from raw_sellers
where seller_id is not null;

