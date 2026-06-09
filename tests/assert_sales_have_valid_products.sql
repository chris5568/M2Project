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
FROM {{ ref('fact_sales') }} f
LEFT JOIN {{ ref('dim_products') }} p 
    ON f.product_key = p.product_key
WHERE p.product_key IS NULL
