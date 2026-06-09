

  create or replace view `assignment-project-498814`.`analytics`.`stg_geolocation`
  OPTIONS()
  as with raw_geo as (
    select * from `assignment-project-498814`.`raw_olist`.`olist_geolocation_dataset`
)
select
    cast(geolocation_zip_code_prefix as string) as zip_code_prefix,
    cast(geolocation_lat as float64) as latitude,
    cast(geolocation_lng as float64) as longitude,
    cast(geolocation_city as string) as city,
    cast(geolocation_state as string) as state
from raw_geo;

