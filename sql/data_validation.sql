-- ==============================================================================
-- POSTGRESQL DATA VALIDATION & INTEGRITY CHECKS
-- ==============================================================================

-- 1. Table Record Counts Audit
SELECT 'dim_geolocation' AS table_name, COUNT(*) AS row_count FROM dim_geolocation
UNION ALL
SELECT 'dim_customers', COUNT(*) FROM dim_customers
UNION ALL
SELECT 'dim_sellers', COUNT(*) FROM dim_sellers
UNION ALL
SELECT 'dim_products', COUNT(*) FROM dim_products
UNION ALL
SELECT 'fact_orders', COUNT(*) FROM fact_orders
UNION ALL
SELECT 'fact_order_items', COUNT(*) FROM fact_order_items
UNION ALL
SELECT 'fact_order_payments', COUNT(*) FROM fact_order_payments
UNION ALL
SELECT 'fact_order_reviews', COUNT(*) FROM fact_order_reviews;

-- 2. Orphan Check: Order items without parent order
SELECT COUNT(*) AS orphan_order_items
FROM fact_order_items i
LEFT JOIN fact_orders o ON i.order_id = o.order_id
WHERE o.order_id IS NULL;

-- 3. Orphan Check: Payments without parent order
SELECT COUNT(*) AS orphan_payments
FROM fact_order_payments p
LEFT JOIN fact_orders o ON p.order_id = o.order_id
WHERE o.order_id IS NULL;

-- 4. Revenue Reconciliation: Total item revenue vs. total payment value
-- (Note: Slight variances can occur due to payment rounding, vouchers or cancelled items)
SELECT 
    ROUND(SUM(price)::numeric, 2) AS total_item_price_revenue,
    ROUND(SUM(freight_value)::numeric, 2) AS total_freight_value,
    ROUND(SUM(total_item_value)::numeric, 2) AS total_item_value_gross,
    (SELECT ROUND(SUM(payment_value)::numeric, 2) FROM fact_order_payments) AS total_payments_captured
FROM fact_order_items;

-- 5. Primary Key Uniqueness Test on Customers
SELECT customer_id, COUNT(*)
FROM dim_customers
GROUP BY customer_id
HAVING COUNT(*) > 1;
