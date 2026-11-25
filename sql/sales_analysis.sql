-- ==============================================================================
-- BUSINESS INTELLIGENCE ANALYTICAL QUERIES (SQL)
-- Meets PRD Section 6 (FR-05) & Section 7 (Dashboard Metrics)
-- ==============================================================================

-- -----------------------------------------------------------------------------
-- 1. Executive Summary KPIs: Total Revenue, Total Orders, Unique Customers, AOV
-- -----------------------------------------------------------------------------
SELECT 
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
    ROUND(SUM(i.price)::numeric, 2) AS total_product_revenue,
    ROUND(SUM(i.freight_value)::numeric, 2) AS total_freight_value,
    ROUND(SUM(i.total_item_value)::numeric, 2) AS total_gross_revenue,
    ROUND((SUM(i.price) / COUNT(DISTINCT o.order_id))::numeric, 2) AS average_order_value_aov
FROM fact_orders o
JOIN fact_order_items i ON o.order_id = i.order_id
JOIN dim_customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered';

-- -----------------------------------------------------------------------------
-- 2. Monthly Revenue Trends & Month-over-Month Growth
-- -----------------------------------------------------------------------------
WITH monthly_sales AS (
    SELECT 
        o.order_year_month,
        COUNT(DISTINCT o.order_id) AS total_monthly_orders,
        ROUND(SUM(i.price)::numeric, 2) AS monthly_revenue
    FROM fact_orders o
    JOIN fact_order_items i ON o.order_id = i.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.order_year_month
)
SELECT 
    order_year_month,
    total_monthly_orders,
    monthly_revenue,
    LAG(monthly_revenue) OVER (ORDER BY order_year_month) AS previous_month_revenue,
    ROUND(
        ((monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY order_year_month)) / 
        NULLIF(LAG(monthly_revenue) OVER (ORDER BY order_year_month), 0) * 100)::numeric, 
        2
    ) AS mom_growth_pct
FROM monthly_sales
ORDER BY order_year_month;

-- -----------------------------------------------------------------------------
-- 3. Top 10 Best-Selling Product Categories by Revenue & Volume
-- -----------------------------------------------------------------------------
SELECT 
    p.product_category_name_english AS category,
    COUNT(i.order_item_id) AS total_units_sold,
    COUNT(DISTINCT o.order_id) AS distinct_orders,
    ROUND(SUM(i.price)::numeric, 2) AS total_revenue,
    ROUND(AVG(i.price)::numeric, 2) AS avg_item_price
FROM fact_orders o
JOIN fact_order_items i ON o.order_id = i.order_id
JOIN dim_products p ON i.product_id = p.product_id
WHERE o.order_status = 'delivered'
GROUP BY p.product_category_name_english
ORDER BY total_revenue DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- 4. Customer Repeat Purchase Behaviour
-- -----------------------------------------------------------------------------
WITH customer_order_counts AS (
    SELECT 
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count,
        SUM(i.price) AS total_spend
    FROM dim_customers c
    JOIN fact_orders o ON c.customer_id = o.customer_id
    JOIN fact_order_items i ON o.order_id = i.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
)
SELECT 
    CASE 
        WHEN order_count = 1 THEN 'One-time Customer'
        WHEN order_count = 2 THEN '2 Orders (Repeat)'
        ELSE '3+ Orders (Loyal)'
    END AS customer_segment,
    COUNT(customer_unique_id) AS customer_count,
    ROUND((COUNT(customer_unique_id) * 100.0 / SUM(COUNT(customer_unique_id)) OVER())::numeric, 2) AS customer_share_pct,
    ROUND(SUM(total_spend)::numeric, 2) AS total_segment_spend,
    ROUND(AVG(total_spend)::numeric, 2) AS avg_spend_per_customer
FROM customer_order_counts
GROUP BY 
    CASE 
        WHEN order_count = 1 THEN 'One-time Customer'
        WHEN order_count = 2 THEN '2 Orders (Repeat)'
        ELSE '3+ Orders (Loyal)'
    END
ORDER BY customer_count DESC;

-- -----------------------------------------------------------------------------
-- 5. Regional Sales Performance: Top States & Cities
-- -----------------------------------------------------------------------------
SELECT 
    c.customer_state AS state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
    ROUND(SUM(i.price)::numeric, 2) AS total_revenue,
    ROUND(AVG(i.price)::numeric, 2) AS avg_order_item_price,
    ROUND(AVG(o.delivery_duration_days)::numeric, 1) AS avg_delivery_days
FROM fact_orders o
JOIN fact_order_items i ON o.order_id = i.order_id
JOIN dim_customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY total_revenue DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- 6. Payment Method Breakdown (Values, Installments, Transaction Share)
-- -----------------------------------------------------------------------------
SELECT 
    payment_type,
    COUNT(order_id) AS transaction_count,
    ROUND(SUM(payment_value)::numeric, 2) AS total_payment_value,
    ROUND((SUM(payment_value) * 100.0 / SUM(SUM(payment_value)) OVER())::numeric, 2) AS payment_share_pct,
    ROUND(AVG(payment_installments)::numeric, 1) AS avg_installments
FROM fact_order_payments
GROUP BY payment_type
ORDER BY total_payment_value DESC;

-- -----------------------------------------------------------------------------
-- 7. Delivery Performance & Customer Satisfaction (Reviews)
-- -----------------------------------------------------------------------------
SELECT 
    r.review_score,
    COUNT(DISTINCT o.order_id) AS order_count,
    ROUND(AVG(o.delivery_duration_days)::numeric, 1) AS avg_delivery_days,
    ROUND(AVG(o.estimated_vs_actual_days)::numeric, 1) AS avg_days_ahead_of_estimate,
    ROUND((SUM(o.is_delayed) * 100.0 / COUNT(o.order_id))::numeric, 2) AS delayed_orders_pct
FROM fact_orders o
JOIN fact_order_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered' AND o.delivery_duration_days IS NOT NULL
GROUP BY r.review_score
ORDER BY r.review_score DESC;
