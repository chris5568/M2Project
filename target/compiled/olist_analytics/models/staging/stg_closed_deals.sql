with raw_deals as (
    select * from `assignment-project-498814`.`raw_olist`.`olist_closed_deals_dataset`
)
select
    cast(mql_id as string) as mql_key,
    cast(seller_id as string) as seller_key,
    safe_cast(won_date as timestamp) as won_at,
    cast(business_segment as string) as business_segment,
    cast(lead_type as string) as lead_type
from raw_deals
where mql_id is not null