# Power BI DAX Measures & Data Model Guide

This guide details the complete data model, relationships, and verified DAX measures to build the **4-Page Interactive E-Commerce Dashboard** in Power BI Desktop.

---

## 🏗️ 1. Data Model Relationships (Star Schema)

When importing the cleaned CSVs from `dataset/cleaned/` into Power BI:

| From (Fact Table) | Foreign Key | To (Dimension Table) | Primary Key | Cardinality | Cross Filter |
|---|---|---|---|---|---|
| `fact_orders` | `customer_id` | `dim_customers` | `customer_id` | Many to 1 (*:1) | Single |
| `fact_order_items` | `order_id` | `fact_orders` | `order_id` | Many to 1 (*:1) | Single |
| `fact_order_items` | `product_id` | `dim_products` | `product_id` | Many to 1 (*:1) | Single |
| `fact_order_items` | `seller_id` | `dim_sellers` | `seller_id` | Many to 1 (*:1) | Single |
| `fact_order_payments` | `order_id` | `fact_orders` | `order_id` | Many to 1 (*:1) | Single |
| `fact_order_reviews` | `order_id` | `fact_orders` | `order_id` | Many to 1 (*:1) | Single |
| `dim_customers` | `customer_zip_code_prefix` | `dim_geolocation` | `zip_code_prefix` | Many to 1 (*:1) | Both/Single |

---

## 📐 2. Core DAX Measures

Create a dedicated table named `_Measures` in Power BI and add the following DAX calculations:

### 💼 Revenue & Sales Measures
```dax
-- Total Net Product Sales Revenue
Total Product Revenue = 
CALCULATE(
    SUM(fact_order_items[price]),
    fact_orders[order_status] = "delivered"
)

-- Total Freight Charges
Total Freight Value = 
CALCULATE(
    SUM(fact_order_items[freight_value]),
    fact_orders[order_status] = "delivered"
)

-- Gross Revenue (Product Sales + Shipping)
Total Gross Revenue = [Total Product Revenue] + [Total Freight Value]

-- Total Distinct Orders
Total Orders = 
CALCULATE(
    DISTINCTCOUNT(fact_orders[order_id]),
    fact_orders[order_status] = "delivered"
)

-- Total Items / Units Sold
Total Units Sold = 
CALCULATE(
    COUNT(fact_order_items[order_item_id]),
    fact_orders[order_status] = "delivered"
)

-- Average Order Value (AOV)
Average Order Value = 
DIVIDE([Total Product Revenue], [Total Orders], 0)
```

### 👥 Customer Analytics Measures
```dax
-- Total Unique Customers
Total Customers = 
CALCULATE(
    DISTINCTCOUNT(dim_customers[customer_unique_id]),
    fact_orders[order_status] = "delivered"
)

-- Repeat Customers Count (Customers with > 1 order)
Repeat Customers Count = 
COUNTROWS(
    FILTER(
        VALUES(dim_customers[customer_unique_id]),
        CALCULATE(DISTINCTCOUNT(fact_orders[order_id]), fact_orders[order_status] = "delivered") > 1
    )
)

-- Repeat Customer Rate (%)
Repeat Customer Rate = 
DIVIDE([Repeat Customers Count], [Total Customers], 0)

-- Average Customer Order Value
Avg Spend Per Customer = 
DIVIDE([Total Product Revenue], [Total Customers], 0)
```

### 🚚 Logistics & Review Scores
```dax
-- Average Delivery Duration (Days)
Avg Delivery Days = 
CALCULATE(
    AVERAGE(fact_orders[delivery_duration_days]),
    fact_orders[order_status] = "delivered",
    NOT(ISBLANK(fact_orders[delivery_duration_days]))
)

-- On-Time Delivery Rate (%)
On Time Delivery Rate = 
DIVIDE(
    CALCULATE(COUNTROWS(fact_orders), fact_orders[is_delayed] = 0, fact_orders[order_status] = "delivered"),
    CALCULATE(COUNTROWS(fact_orders), fact_orders[order_status] = "delivered"),
    0
)

-- Average Review Score (1 to 5 Stars)
Average Review Score = 
CALCULATE(
    AVERAGE(fact_order_reviews[review_score]),
    fact_orders[order_status] = "delivered"
)
```

---

## 📊 3. Dashboard Page Architecture

### 📄 Page 1: Sales Overview (Executive View)
- **Top KPIs**: `Total Product Revenue` ($13.22M), `Total Orders` (96.5K), `Unique Customers` (93.4K), `Average Order Value` ($137.04).
- **Visuals**:
  1. *Line & Clustered Column Chart*: Monthly Revenue & Orders (`fact_orders[order_year_month]` vs `[Total Product Revenue]` & `[Total Orders]`).
  2. *Donut Chart*: Payment Method Distribution (`fact_order_payments[payment_type]` vs `[Total Payment Value]`).
  3. *Bar Chart*: Top 5 Categories by Revenue.
  4. *Card / Funnel Chart*: Order Fulfillment Status (`fact_orders[order_status]`).
- **Slicers**: Year / Month, Order Status.

### 📄 Page 2: Product Performance Analysis
- **Top KPIs**: `Total Products Sold` (32,951), `Total Categories` (71), `Top Selling Category` ("Health Beauty").
- **Visuals**:
  1. *Horizontal Clustered Bar Chart*: Top 10 Product Categories by Revenue.
  2. *Scatter Plot*: Average Item Price vs Units Sold by Product Category (Identifies volume drivers vs premium high-ticket items).
  3. *Matrix*: Category Breakdown (Category, Units Sold, Total Revenue, Avg Freight Cost, Avg Review Score).
- **Slicers**: Category Multi-select, Price Range.

### 📄 Page 3: Customer Behavior & Retention
- **Top KPIs**: `Total Customers` (93,358), `Repeat Customers` (2,801), `Repeat Customer Rate` (3.00%), `Avg Spend per Customer` ($141.62).
- **Visuals**:
  1. *Donut Chart*: Customer Segmentation (One-time vs Repeat vs Loyal Customers).
  2. *Tree Map*: Customer Share by Top States (SP, RJ, MG, RS, PR).
  3. *Line Chart*: New Customer Acquisition Trend over time.
- **Slicers**: Customer State, Customer City.

### 📄 Page 4: Regional & Logistics Performance
- **Top KPIs**: `Active States` (27), `Top State` (São Paulo - $5.07M), `On-Time Delivery %` (92.5%), `Avg Delivery Time` (12.1 Days).
- **Visuals**:
  1. *Filled Map / Shape Map*: Brazilian States by Total Sales Revenue.
  2. *Clustered Bar Chart*: Average Delivery Days by Destination State (comparing SE/South vs North/Northeast states).
  3. *Grouped Bar Chart*: Correlation between Review Score (1-5) and Delivery Delay % (shows 1-star reviews average 21.3 days vs 10.7 days for 5-star).
- **Slicers**: State, Delay Status (`is_delayed`).
