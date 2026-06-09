
    
    

with dbt_test__target as (

  select sales_key as unique_field
  from `assignment-project-498814`.`analytics`.`fact_sales`
  where sales_key is not null

)

select
    unique_field,
    count(*) as n_records

from dbt_test__target
group by unique_field
having count(*) > 1


