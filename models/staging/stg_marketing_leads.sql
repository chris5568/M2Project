with raw_leads as (
    select * from {{ source('raw_olist', 'olist_marketing_qualified_leads_dataset') }}
)
select
    cast(mql_id as string) as mql_key,
    safe_cast(first_contact_date as date) as first_contact_date,
    cast(landing_page_id as string) as landing_page_id,
    cast(origin as string) as origin
from raw_leads
where mql_id is not null
