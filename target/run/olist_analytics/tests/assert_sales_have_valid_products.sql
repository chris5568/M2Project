
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- ==============================================================================
-- [Referential Integrity Test 3]: Structural Relational Linkage Audit
-- Business Goal: Catches orphaned records by verifying every product sold in 
--                fact_sales maps back to a valid entry inside dim_products.
-- ==============================================================================

-- This test looks for orphaned records. 
-- It returns any sales rows that point to a product_key that does not exist in our products dimension.

SELECT 
    f.order_id,
    f.product_key
FROM `assignment-project-498814`.`analytics`.`fact_sales` f
LEFT JOIN `assignment-project-498814`.`analytics`.`dim_products` p 
    ON f.product_key = p.product_key
WHERE p.product_key IS NULL
  
  
      
    ) dbt_internal_test