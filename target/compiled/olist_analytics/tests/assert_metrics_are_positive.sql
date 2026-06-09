-- ==============================================================================
-- [Logical Integrity Test 2]: Financial Metric Safeguard Validation
-- Business Goal: Audits fact_sales and dim_customers to ensure critical metrics 
--                (revenue and spend) are never negative numbers.
-- ==============================================================================

-- This test checks for logical flaws. If any rows are returned, a metric is negative, which fails the test.

SELECT 
    'fact_sales_negative_prices' as test_name,
    COUNT(*) as failure_count
FROM `assignment-project-498814`.`analytics`.`fact_sales`
WHERE total_sale_amount < 0
HAVING COUNT(*) > 0

UNION ALL

SELECT 
    'dim_customers_negative_spend' as test_name,
    COUNT(*) as failure_count
FROM `assignment-project-498814`.`analytics`.`dim_customers`
WHERE lifetime_spend < 0
HAVING COUNT(*) > 0