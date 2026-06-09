

  create or replace view `assignment-project-498814`.`analytics`.`stg_order_reviews`
  OPTIONS()
  as with raw_reviews as (
    select * from `assignment-project-498814`.`raw_olist`.`olist_order_reviews_dataset`
)
select
    cast(review_id as string) as review_id,
    cast(order_id as string) as order_id,
    cast(review_score as int64) as review_score,
    cast(review_comment_title as string) as comment_title,
    safe_cast(review_creation_date as timestamp) as review_created_at
from raw_reviews
where review_id is not null;

