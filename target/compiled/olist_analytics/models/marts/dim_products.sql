with raw_products as (
    select * from `assignment-project-498814`.`raw_olist`.`olist_products_dataset`
),
translations as (
    select * from `assignment-project-498814`.`analytics`.`stg_category_translation`
)
select
    cast(p.product_id as string) as product_key,
    coalesce(t.category_name_en, p.product_category_name, 'unknown') as category_name,
    cast(p.product_weight_g as float64) as weight_g
from raw_products p
left join translations t on p.product_category_name = t.category_name_pt