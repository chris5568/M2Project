with raw_translation as (
    select * from {{ source('raw_olist', 'product_category_name_translation') }}
)
select
    cast(product_category_name as string) as category_name_pt,
    cast(product_category_name_english as string) as category_name_en
from raw_translation
