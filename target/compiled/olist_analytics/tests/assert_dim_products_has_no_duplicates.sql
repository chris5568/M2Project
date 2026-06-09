-- ==============================================================================
-- [Deduplication Test 1]: Product Catalog Inflation Audit
-- Business Goal: Audits dim_products to ensure every unique inventory item appears exactly once.
-- ==============================================================================

-- If this query returns rows, the test fails. It audits if any product_key appears more than once.
SELECT 
    product_key, 
    COUNT(*) as records_found
FROM `assignment-project-498814`.`analytics`.`dim_products`
GROUP BY product_key
HAVING COUNT(*) > 1