"""
PostgreSQL Ingestion Script for Olist Cleaned Star-Schema Tables.
Usage:
    python load_to_postgres.py --dbname ecommerce_db --user postgres --password YOUR_PASS --host localhost --port 5432
"""

import os
import sys
import argparse
import pandas as pd
from sqlalchemy import create_engine, text

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANED_DIR = os.path.join(BASE_DIR, "dataset", "cleaned")
SQL_DIR = os.path.join(BASE_DIR, "sql")

LOAD_SEQUENCE = [
    ("dim_geolocation", "dim_geolocation.csv"),
    ("dim_customers", "dim_customers.csv"),
    ("dim_sellers", "dim_sellers.csv"),
    ("dim_products", "dim_products.csv"),
    ("fact_orders", "fact_orders.csv"),
    ("fact_order_items", "fact_order_items.csv"),
    ("fact_order_payments", "fact_order_payments.csv"),
    ("fact_order_reviews", "fact_order_reviews.csv")
]

def load_data(db_url):
    print(f"Connecting to database via SQLAlchemy...")
    engine = create_engine(db_url)

    # 1. Execute schema.sql to create tables and constraints
    schema_path = os.path.join(SQL_DIR, "schema.sql")
    print(f"Executing schema from {schema_path}...")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with engine.begin() as conn:
        for statement in schema_sql.split(";"):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))
    print("[+] Database schema created successfully.")

    # 2. Ingest CSV data in sequence
    for table_name, csv_file in LOAD_SEQUENCE:
        csv_path = os.path.join(CLEANED_DIR, csv_file)
        if not os.path.exists(csv_path):
            print(f"[!] Warning: File {csv_file} does not exist, skipping.")
            continue

        print(f"Loading {csv_file} into {table_name}...")
        df = pd.read_csv(csv_path)
        
        # Ingest using chunksize for memory efficiency
        df.to_sql(table_name, engine, if_exists="append", index=False, chunksize=10000)
        print(f"    [+] Successfully loaded {len(df):,} rows into {table_name}.")

    print("\n[✔] All data loaded successfully into PostgreSQL.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load cleaned e-commerce data into PostgreSQL")
    parser.add_argument("--host", default="localhost", help="Database host")
    parser.add_argument("--port", default="5432", help="Database port")
    parser.add_argument("--dbname", default="ecommerce_db", help="Database name")
    parser.add_argument("--user", default="postgres", help="Database username")
    parser.add_argument("--password", default="", help="Database password")

    args = parser.parse_args()
    connection_string = f"postgresql://{args.user}:{args.password}@{args.host}:{args.port}/{args.dbname}"
    try:
        load_data(connection_string)
    except Exception as e:
        print(f"Error loading to PostgreSQL: {e}")
        print("Note: If PostgreSQL is not installed locally, you can load these cleaned CSVs directly into Power BI.")
