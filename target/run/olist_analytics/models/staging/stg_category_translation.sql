

  create or replace view `assignment-project-498814`.`analytics`.`stg_category_translation`
  OPTIONS()
  as with raw_translation as (
    select * from `assignment-project-498814`.`raw_olist`.`product_category_name_translation`
)
select
    cast(product_category_name as string) as category_name_pt,
    cast(product_category_name_english as string) as category_name_en
from raw_translation;

