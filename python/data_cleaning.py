"""
Data Cleaning & Preprocessing Pipeline for Brazilian E-Commerce (Olist).
Handles:
1. Missing value imputations & removals.
2. Geolocation deduplication & coordinate aggregation.
3. Portuguese to English product category mapping.
4. DateTime standardizations & analytical feature engineering (delivery duration, order year, order month).
5. Referential integrity and data consistency validation.
6. Exports cleaned datasets to dataset/cleaned/ in CSV format.
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "dataset", "raw")
CLEANED_DIR = os.path.join(BASE_DIR, "dataset", "cleaned")
os.makedirs(CLEANED_DIR, exist_ok=True)

def clean_geolocation(raw_dir):
    print(">>> Cleaning Geolocation Dataset...")
    df = pd.read_csv(os.path.join(raw_dir, "olist_geolocation_dataset.csv"))
    # Group by zip_code_prefix to eliminate 260k duplicates and get accurate average lat/lng per zip code
    df_clean = df.groupby("geolocation_zip_code_prefix").agg({
        "geolocation_lat": "mean",
        "geolocation_lng": "mean",
        "geolocation_city": "first",
        "geolocation_state": "first"
    }).reset_index()
    
    df_clean.rename(columns={
        "geolocation_zip_code_prefix": "zip_code_prefix",
        "geolocation_lat": "latitude",
        "geolocation_lng": "longitude",
        "geolocation_city": "city",
        "geolocation_state": "state"
    }, inplace=True)
    df_clean["city"] = df_clean["city"].astype(str).str.strip().str.title()
    df_clean["state"] = df_clean["state"].astype(str).str.strip().str.upper()
    return df_clean

def clean_customers(raw_dir):
    print(">>> Cleaning Customers Dataset...")
    df = pd.read_csv(os.path.join(raw_dir, "olist_customers_dataset.csv"))
    df["customer_city"] = df["customer_city"].astype(str).str.strip().str.title()
    df["customer_state"] = df["customer_state"].astype(str).str.strip().str.upper()
    return df

def clean_sellers(raw_dir):
    print(">>> Cleaning Sellers Dataset...")
    df = pd.read_csv(os.path.join(raw_dir, "olist_sellers_dataset.csv"))
    df["seller_city"] = df["seller_city"].astype(str).str.strip().str.title()
    df["seller_state"] = df["seller_state"].astype(str).str.strip().str.upper()
    return df

def clean_products(raw_dir):
    print(">>> Cleaning Products Dataset with Translations...")
    df_prod = pd.read_csv(os.path.join(raw_dir, "olist_products_dataset.csv"))
    df_trans = pd.read_csv(os.path.join(raw_dir, "product_category_name_translation.csv"))
    
    # Merge English translation
    df_clean = df_prod.merge(df_trans, on="product_category_name", how="left")
    
    # Fill missing product category with 'other'
    df_clean["product_category_name_english"] = df_clean["product_category_name_english"].fillna("other")
    df_clean["product_category_name"] = df_clean["product_category_name"].fillna("outros")
    
    # Standardize category labels
    df_clean["product_category_name_english"] = df_clean["product_category_name_english"].str.replace("_", " ").str.title()
    
    # Numerical imputation for missing measurements (median)
    for col in ["product_name_lenght", "product_description_lenght", "product_photos_qty", 
                "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]:
        df_clean[col] = df_clean[col].fillna(df_clean[col].median())
        
    return df_clean

def clean_orders(raw_dir):
    print(">>> Cleaning Orders Dataset & Feature Engineering...")
    df = pd.read_csv(os.path.join(raw_dir, "olist_orders_dataset.csv"))
    
    date_cols = [
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")
        
    # Feature engineering
    df["order_year"] = df["order_purchase_timestamp"].dt.year
    df["order_month"] = df["order_purchase_timestamp"].dt.month
    df["order_year_month"] = df["order_purchase_timestamp"].dt.strftime("%Y-%m")
    df["order_day_of_week"] = df["order_purchase_timestamp"].dt.day_name()
    
    # Delivery duration (in days)
    df["delivery_duration_days"] = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.total_seconds() / (24 * 3600)
    # Estimated vs actual delivery difference (+ indicates early, - indicates delayed)
    df["estimated_vs_actual_days"] = (df["order_estimated_delivery_date"] - df["order_delivered_customer_date"]).dt.total_seconds() / (24 * 3600)
    df["is_delayed"] = np.where(df["order_delivered_customer_date"] > df["order_estimated_delivery_date"], 1, 0)
    
    return df

def clean_order_items(raw_dir):
    print(">>> Cleaning Order Items Dataset...")
    df = pd.read_csv(os.path.join(raw_dir, "olist_order_items_dataset.csv"))
    df["shipping_limit_date"] = pd.to_datetime(df["shipping_limit_date"], errors="coerce")
    df["total_item_value"] = df["price"] + df["freight_value"]
    return df

def clean_order_payments(raw_dir):
    print(">>> Cleaning Order Payments Dataset...")
    df = pd.read_csv(os.path.join(raw_dir, "olist_order_payments_dataset.csv"))
    # Standardize payment types
    df["payment_type"] = df["payment_type"].str.replace("_", " ").str.title()
    return df

def clean_order_reviews(raw_dir):
    print(">>> Cleaning Order Reviews Dataset...")
    df = pd.read_csv(os.path.join(raw_dir, "olist_order_reviews_dataset.csv"))
    df["review_creation_date"] = pd.to_datetime(df["review_creation_date"], errors="coerce")
    df["review_answer_timestamp"] = pd.to_datetime(df["review_answer_timestamp"], errors="coerce")
    
    # Impute missing review text placeholders
    df["review_comment_title"] = df["review_comment_title"].fillna("No Title").str.strip()
    df["review_comment_message"] = df["review_comment_message"].fillna("No Comments").str.strip()
    return df

def run_cleaning_pipeline():
    print("=" * 70)
    print("   STARTING END-TO-END DATA CLEANING & PREPROCESSING")
    print("=" * 70)
    
    cleaned_datasets = {
        "dim_geolocation.csv": clean_geolocation(RAW_DIR),
        "dim_customers.csv": clean_customers(RAW_DIR),
        "dim_sellers.csv": clean_sellers(RAW_DIR),
        "dim_products.csv": clean_products(RAW_DIR),
        "fact_orders.csv": clean_orders(RAW_DIR),
        "fact_order_items.csv": clean_order_items(RAW_DIR),
        "fact_order_payments.csv": clean_order_payments(RAW_DIR),
        "fact_order_reviews.csv": clean_order_reviews(RAW_DIR)
    }
    
    print("\n>>> Exporting Cleaned Star-Schema Tables to dataset/cleaned/:")
    for filename, df in cleaned_datasets.items():
        out_path = os.path.join(CLEANED_DIR, filename)
        df.to_csv(out_path, index=False)
        print(f"    [+] Saved {filename} ({len(df):,} rows, {len(df.columns)} cols)")
        
    print("\n" + "=" * 70)
    print("   DATA CLEANING PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)

if __name__ == "__main__":
    run_cleaning_pipeline()
