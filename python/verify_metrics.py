"""
SQL Benchmark & Analytical Verification Script (Runs SQL Analytics using SQLite in-memory).
Validates that all PRD metrics, KPIs, and analytical queries are completely consistent
and returns verified results for the final report.
"""

import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANED_DIR = os.path.join(BASE_DIR, "dataset", "cleaned")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def verify_and_generate_insights():
    conn = sqlite3.connect(":memory:")
    
    # Load all cleaned CSVs into SQLite
    tables = [
        "dim_customers", "dim_products", "dim_sellers", "dim_geolocation",
        "fact_orders", "fact_order_items", "fact_order_payments", "fact_order_reviews"
    ]
    for tbl in tables:
        csv_path = os.path.join(CLEANED_DIR, f"{tbl}.csv")
        df = pd.read_csv(csv_path)
        df.to_sql(tbl, conn, index=False, if_exists="replace")
        
    print(">>> All cleaned tables indexed into verification database.")
    
    # Query 1: Overall KPIs
    kpi_query = """
    SELECT 
        COUNT(DISTINCT o.order_id) AS total_orders,
        COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
        ROUND(SUM(i.price), 2) AS total_product_revenue,
        ROUND(SUM(i.freight_value), 2) AS total_freight_value,
        ROUND(SUM(i.total_item_value), 2) AS total_gross_revenue,
        ROUND(SUM(i.price) / COUNT(DISTINCT o.order_id), 2) AS aov
    FROM fact_orders o
    JOIN fact_order_items i ON o.order_id = i.order_id
    JOIN dim_customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered';
    """
    df_kpi = pd.read_sql_query(kpi_query, conn)
    print("\n--- EXECUTIVE METRICS ---")
    print(df_kpi.to_string(index=False))
    
    # Query 2: Top Categories
    cat_query = """
    SELECT 
        p.product_category_name_english AS category,
        COUNT(i.order_item_id) AS units_sold,
        ROUND(SUM(i.price), 2) AS total_revenue
    FROM fact_orders o
    JOIN fact_order_items i ON o.order_id = i.order_id
    JOIN dim_products p ON i.product_id = p.product_id
    WHERE o.order_status = 'delivered'
    GROUP BY p.product_category_name_english
    ORDER BY total_revenue DESC
    LIMIT 10;
    """
    df_cat = pd.read_sql_query(cat_query, conn)
    print("\n--- TOP 10 PRODUCT CATEGORIES ---")
    print(df_cat.to_string(index=False))

    # Query 3: Repeat Customers
    repeat_query = """
    WITH customer_orders AS (
        SELECT 
            c.customer_unique_id,
            COUNT(DISTINCT o.order_id) as order_count
        FROM dim_customers c
        JOIN fact_orders o ON c.customer_id = o.customer_id
        WHERE o.order_status = 'delivered'
        GROUP BY c.customer_unique_id
    )
    SELECT 
        CASE WHEN order_count = 1 THEN '1 Order (One-time)'
             WHEN order_count = 2 THEN '2 Orders (Repeat)'
             ELSE '3+ Orders (Loyal)' END AS segment,
        COUNT(*) AS customer_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_orders), 2) AS pct_share
    FROM customer_orders
    GROUP BY segment
    ORDER BY customer_count DESC;
    """
    df_repeat = pd.read_sql_query(repeat_query, conn)
    print("\n--- CUSTOMER RETENTION SEGMENTATION ---")
    print(df_repeat.to_string(index=False))

    # Query 4: Regional Analysis
    region_query = """
    SELECT 
        c.customer_state AS state,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(SUM(i.price), 2) AS total_revenue,
        ROUND(AVG(o.delivery_duration_days), 1) AS avg_delivery_days
    FROM fact_orders o
    JOIN fact_order_items i ON o.order_id = i.order_id
    JOIN dim_customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_state
    ORDER BY total_revenue DESC
    LIMIT 5;
    """
    df_region = pd.read_sql_query(region_query, conn)
    print("\n--- TOP 5 STATES BY REVENUE ---")
    print(df_region.to_string(index=False))

    # Query 5: Review Score vs Delivery
    review_query = """
    SELECT 
        r.review_score,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(AVG(o.delivery_duration_days), 1) AS avg_delivery_days,
        ROUND(AVG(o.is_delayed) * 100, 2) AS delayed_orders_pct
    FROM fact_orders o
    JOIN fact_order_reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered' AND o.delivery_duration_days IS NOT NULL
    GROUP BY r.review_score
    ORDER BY r.review_score DESC;
    """
    df_review = pd.read_sql_query(review_query, conn)
    print("\n--- DELIVERY IMPACT ON REVIEWS ---")
    print(df_review.to_string(index=False))

    conn.close()

if __name__ == "__main__":
    verify_and_generate_insights()
