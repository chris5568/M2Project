with leads as (
    select * from {{ ref('stg_marketing_leads') }}
),
deals as (
    select * from {{ ref('stg_closed_deals') }}
)
select
    l.mql_key,
    l.first_contact_date,
    l.origin,
    d.seller_key,
    d.business_segment,
    d.lead_type,
    case when d.seller_key is not null then 1 else 0 end as is_converted_deal
from leads l
left join deals d on l.mql_key = d.mql_key
