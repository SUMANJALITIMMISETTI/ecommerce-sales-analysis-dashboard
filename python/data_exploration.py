"""
Exploratory Data Analysis (EDA) Script for Olist Brazilian E-Commerce Dataset.
Scans raw CSV files, inspects shapes, null values, data types, duplicate records,
and key relationships across tables.
"""

import os
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "dataset", "raw")

FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv"
}

def explore_dataset():
    print("=" * 70)
    print("   BRAZILIAN E-COMMERCE DATASET EXPLORATION & AUDIT REPORT")
    print("=" * 70)
    
    summary = {}

    for name, filename in FILES.items():
        filepath = os.path.join(RAW_DIR, filename)
        if not os.path.exists(filepath):
            print(f"[!] File not found: {filename}")
            continue

        print(f"\n>>> Analyzing: {name} ({filename})")
        df = pd.read_csv(filepath)
        row_count, col_count = df.shape
        duplicates = df.duplicated().sum()
        null_counts = df.isnull().sum()
        cols_with_nulls = null_counts[null_counts > 0]

        summary[name] = {
            "rows": row_count,
            "columns": col_count,
            "duplicates": duplicates,
            "cols_with_nulls": cols_with_nulls.to_dict()
        }

        print(f"    - Dimensions: {row_count:,} rows, {col_count} columns")
        print(f"    - Exact Duplicates: {duplicates:,}")
        if not cols_with_nulls.empty:
            print("    - Null values per column:")
            for col, count in cols_with_nulls.items():
                pct = (count / row_count) * 100
                print(f"        * {col}: {count:,} ({pct:.2f}%)")
        else:
            print("    - Null values: None detected")

    print("\n" + "=" * 70)
    print("   RELATIONAL INTEGRITY CHECK")
    print("=" * 70)

    orders_df = pd.read_csv(os.path.join(RAW_DIR, FILES["orders"]))
    customers_df = pd.read_csv(os.path.join(RAW_DIR, FILES["customers"]))
    items_df = pd.read_csv(os.path.join(RAW_DIR, FILES["order_items"]))
    payments_df = pd.read_csv(os.path.join(RAW_DIR, FILES["order_payments"]))

    # Key validation
    missing_cust_in_orders = ~orders_df["customer_id"].isin(customers_df["customer_id"])
    print(f"- Orders with unknown customer_id: {missing_cust_in_orders.sum()}")

    missing_orders_in_items = ~items_df["order_id"].isin(orders_df["order_id"])
    print(f"- Order Items with unknown order_id: {missing_orders_in_items.sum()}")

    missing_orders_in_payments = ~payments_df["order_id"].isin(orders_df["order_id"])
    print(f"- Payments with unknown order_id: {missing_orders_in_payments.sum()}")

    # Date ranges
    orders_df["order_purchase_timestamp"] = pd.to_datetime(orders_df["order_purchase_timestamp"])
    print(f"- Date Range: {orders_df['order_purchase_timestamp'].min()} to {orders_df['order_purchase_timestamp'].max()}")
    print(f"- Distinct Orders: {orders_df['order_id'].nunique():,}")
    print(f"- Distinct Customers (unique): {customers_df['customer_unique_id'].nunique():,}")

    print("\nExploration completed successfully.")

if __name__ == "__main__":
    explore_dataset()
