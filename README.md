# End-to-End E-Commerce Sales Analysis & Business Intelligence Dashboard

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-blue.svg)](https://www.postgresql.org/)
[![Power BI](https://img.shields.io/badge/Power_BI-Desktop-F2C811.svg)](https://powerbi.microsoft.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, end-to-end Data Analytics and Business Intelligence project analyzing real-world transactional data from the **Olist Brazilian E-Commerce Public Dataset** (99,441 orders spanning 2016–2018).

---

## 📊 Project Overview

This project implements the complete data analytics lifecycle:
1. **Data Ingestion & Quality Audit (Python):** Explored 9 raw relational datasets, handling missing values, standardizing datetime fields, and resolving 260k+ geolocation redundancies.
2. **ETL & Data Cleaning Pipeline (Pandas / NumPy):** Engineered key features including delivery duration, delay flags, and Portuguese-to-English translations; exported clean Star-Schema tables.
3. **Relational Database Modeling (PostgreSQL):** Designed normalized snowflake/star schema with primary/foreign keys, indexes, and referential constraints.
4. **Business Analytics (SQL):** Analyzed sales velocity, customer retention rates, monthly trends, and delivery impact on customer sentiment.
5. **Interactive Business Intelligence (Power BI):** Designed a 4-page executive dashboard with advanced DAX measures.

---

## 📈 Key Business Metrics Reconciled

| Business Metric | Value | Definition & Reconciled Basis |
|---|---|---|
| **Total Gross Revenue** | **$15,419,773.75** | Product items total ($13.22M) + freight value ($2.20M) |
| **Total Product Revenue** | **$13,221,498.11** | Sum of delivered order item prices |
| **Total Completed Orders** | **96,478** | Count of distinct orders with status `delivered` |
| **Average Order Value (AOV)** | **$137.04** | Total Product Revenue / Total Completed Orders |
| **Unique Customers** | **93,358** | Count of distinct `customer_unique_id` |
| **Repeat Customer Rate** | **3.00%** | Customers with 2+ completed orders (2,801 customers) |
| **On-Time Delivery Rate** | **92.5%** | Delivered on or before estimated date |
| **Average Delivery Duration** | **12.1 Days** | Actual delivery timestamp minus purchase timestamp |

---

## 🏗️ Architecture & Star Schema

```
                           ┌───────────────────┐
                           │  dim_geolocation  │
                           └─────────┬─────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           │                           ▼
┌──────────────────┐                 │                 ┌──────────────────┐
│  dim_customers   │                 │                 │   dim_sellers    │
└────────┬─────────┘                 │                 └────────┬─────────┘
         │                           │                          │
         ▼                           ▼                          ▼
┌──────────────────┐       ┌───────────────────┐       ┌──────────────────┐
│   fact_orders    │◄──────┤ fact_order_items  ├──────►│   dim_products   │
└────────┬─────────┘       └───────────────────┘       └──────────────────┘
         │
         ├───────────────────────────┐
         ▼                           ▼
┌──────────────────┐       ┌───────────────────┐
│fact_order_payment│       │fact_order_reviews │
└──────────────────┘       └───────────────────┘
```

---

## 📂 Project Structure

```text
├── dataset/
│   ├── raw/                      # Original Olist CSV files
│   └── cleaned/                  # 8 clean Star-Schema CSVs (dim_* & fact_*)
│
├── python/
│   ├── data_exploration.py       # Automated EDA & data quality auditor
│   ├── data_cleaning.py          # Preprocessing, translation & feature engineering pipeline
│   ├── load_to_postgres.py       # Automated PostgreSQL bulk loader
│   └── verify_metrics.py         # In-memory SQL verification benchmark
│
├── sql/
│   ├── schema.sql                # Relational DDL with PK/FK constraints & indexes
│   ├── data_validation.sql       # Quality control, orphan checks & revenue reconciliation
│   └── sales_analysis.sql        # Business queries (FR-05 & KPI metrics)
│
├── powerbi/
│   └── dax_measures.md           # Complete DAX formulas and 4-page dashboard specification
│
├── reports/
│   └── business_insights.md      # Detailed executive takeaways & operational strategy
│
├── screenshots/                  # Dashboard previews & visual mockups
└── README.md
```

---

## 💻 How to Run the Project

### 1. Set Up Python Environment
Ensure Python 3.10+ is installed:
```powershell
pip install pandas numpy sqlalchemy psycopg2-binary
```

### 2. Run Data Exploration & Cleaning Pipeline
```powershell
# 1. Audit raw data
python python/data_exploration.py

# 2. Run ETL pipeline and export to dataset/cleaned/
python python/data_cleaning.py

# 3. Verify metrics and analytics via SQL benchmark
python python/verify_metrics.py
```

### 3. Load into PostgreSQL (Optional)
```powershell
python python/load_to_postgres.py --dbname ecommerce_db --user postgres --password YOUR_PASSWORD
```

### 4. Build / Open in Power BI
1. Open **Power BI Desktop**.
2. Select **Get Data** -> **Folder** or **CSV/Text** and select the files inside `dataset/cleaned/`.
3. Open [`powerbi/dax_measures.md`](file:///powerbi/dax_measures.md) to copy the pre-built DAX measures into your report.
4. Follow the 4-page layout specifications for **Sales Overview**, **Product Analysis**, **Customer Analysis**, and **Regional Analysis**.

---

## 📄 Deliverables Checklist

- [x] Raw Olist datasets stored & verified in `dataset/raw/`
- [x] Automated Python exploration script (`data_exploration.py`)
- [x] Complete Python cleaning & feature engineering script (`data_cleaning.py`)
- [x] Cleaned star-schema datasets in `dataset/cleaned/`
- [x] PostgreSQL schema DDL with constraints & indexes (`schema.sql`)
- [x] PostgreSQL automated loading script (`load_to_postgres.py`)
- [x] Data validation & reconciliation SQL suite (`data_validation.sql`)
- [x] Analytical SQL queries addressing all PRD business questions (`sales_analysis.sql`)
- [x] Power BI DAX measures & 4-page architecture guide (`dax_measures.md`)
- [x] Executive Business Insights & Strategy Report (`reports/business_insights.md`)
- [x] Comprehensive, portfolio-ready `README.md`
