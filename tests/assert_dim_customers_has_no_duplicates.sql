-- ==============================================================================
-- [Deduplication Test 1]: Customer Grain Control Validation
-- Business Goal: Audits dim_customers to ensure no customer_key is duplicated.
-- ==============================================================================

-- If this query returns rows, the test fails. It audits if any customer_key appears more than once.
SELECT 
    customer_key, 
    COUNT(*) as records_found
FROM {{ ref('dim_customers') }}
GROUP BY customer_key
HAVING COUNT(*) > 1
