# Step-by-Step Guide to Build the Power BI Dashboard (.pbix)

This step-by-step checklist will guide you through creating `ecommerce_dashboard.pbix` in Power BI Desktop in under 15 minutes.

---

## 🚀 Step 1: Open Power BI Desktop & Load Data

1. Launch **Power BI Desktop** from your Windows Start Menu.
2. In the top ribbon, click **Get Data** ➔ **Folder** (or **Text/CSV**).
3. Browse to your project folder:
   ```
   c:\Users\SUMANJALI\Desktop\End-to-End E-Commerce Sales Analysis & Business Intelligence Dashboard\dataset\cleaned\
   ```
4. Click **Combine & Transform Data** (or load each of the 8 CSV files):
   - `dim_customers.csv`
   - `dim_products.csv`
   - `dim_sellers.csv`
   - `dim_geolocation.csv`
   - `fact_orders.csv`
   - `fact_order_items.csv`
   - `fact_order_payments.csv`
   - `fact_order_reviews.csv`
5. Click **Close & Apply**.

---

## 🔗 Step 2: Verify Relationships (Model View)

Switch to the **Model View** (icon on the left sidebar):
Ensure the following relationships exist (Power BI often detects them automatically):
- `fact_orders[customer_id]` ──▶ `dim_customers[customer_id]` (1:*)
- `fact_order_items[order_id]` ──▶ `fact_orders[order_id]` (1:*)
- `fact_order_items[product_id]` ──▶ `dim_products[product_id]` (1:*)
- `fact_order_items[seller_id]` ──▶ `dim_sellers[seller_id]` (1:*)
- `fact_order_payments[order_id]` ──▶ `fact_orders[order_id]` (1:*)
- `fact_order_reviews[order_id]` ──▶ `fact_orders[order_id]` (1:*)

---

## 🧮 Step 3: Create Key DAX Measures

Click **Enter Data** to create a blank table named `_Measures`. Then right-click it, select **New Measure**, and paste each from [dax_measures.md](file:///c:/Users/SUMANJALI/Desktop/End-to-End%20E-Commerce%20Sales%20Analysis%20&%20Business%20Intelligence%20Dashboard/powerbi/dax_measures.md):

1. **Total Product Revenue**:
   ```dax
   Total Product Revenue = CALCULATE(SUM(fact_order_items[price]), fact_orders[order_status] = "delivered")
   ```
2. **Total Orders**:
   ```dax
   Total Orders = CALCULATE(DISTINCTCOUNT(fact_orders[order_id]), fact_orders[order_status] = "delivered")
   ```
3. **Average Order Value (AOV)**:
   ```dax
   Average Order Value = DIVIDE([Total Product Revenue], [Total Orders], 0)
   ```
4. **Unique Customers**:
   ```dax
   Total Customers = CALCULATE(DISTINCTCOUNT(dim_customers[customer_unique_id]), fact_orders[order_status] = "delivered")
   ```
5. **Avg Delivery Days**:
   ```dax
   Avg Delivery Days = CALCULATE(AVERAGE(fact_orders[delivery_duration_days]), fact_orders[order_status] = "delivered")
   ```

---

## 🎨 Step 4: Build the 4 Pages

### 📄 Page 1: Sales Overview
- **Rename page to**: `Sales Overview`
- **KPI Cards (top)**: 
  - Card 1: `[Total Product Revenue]` ($13.22M)
  - Card 2: `[Total Orders]` (96.5K)
  - Card 3: `[Total Customers]` (93.4K)
  - Card 4: `[Average Order Value]` ($137.04)
- **Line & Stacked Column Chart**:
  - X-axis: `fact_orders[order_year_month]`
  - Column Y-axis: `[Total Product Revenue]`
  - Line Y-axis: `[Total Orders]`
- **Donut Chart**:
  - Legend: `fact_order_payments[payment_type]`
  - Values: `fact_order_payments[payment_value]`
- **Slicer**: `fact_orders[order_year]`

### 📄 Page 2: Product Analysis
- **Rename page to**: `Product Analysis`
- **Horizontal Clustered Bar Chart**:
  - Y-axis: `dim_products[product_category_name_english]`
  - X-axis: `[Total Product Revenue]`
  - Filter: Top 10 by `[Total Product Revenue]`
- **Scatter Chart**:
  - Values: `dim_products[product_category_name_english]`
  - X-axis: `[Total Units Sold]`
  - Y-axis: `Average Price`
- **Table / Matrix**:
  - Category, Units Sold, Revenue, Avg Freight

### 📄 Page 3: Customer Analysis
- **Rename page to**: `Customer Analysis`
- **KPI Cards**: `Total Customers` (93,358), `Repeat Customers` (2,801), `Repeat Rate` (3.0%)
- **Donut Chart**:
  - Legend: One-time vs. Repeat Customers
  - Values: Count of customers
- **Tree Map**:
  - Category: `dim_customers[customer_state]`
  - Values: `[Total Customers]`

### 📄 Page 4: Regional & Logistics Analysis
- **Rename page to**: `Regional & Logistics Analysis`
- **Map / Filled Map**:
  - Location: `dim_customers[customer_state]`
  - Bubble size / Tooltip: `[Total Product Revenue]`
- **Clustered Bar Chart**:
  - Y-axis: `dim_customers[customer_state]`
  - X-axis: `[Avg Delivery Days]`
- **Clustered Column Chart**:
  - X-axis: `fact_order_reviews[review_score]`
  - Y-axis: `[Avg Delivery Days]`

---

## 💾 Step 5: Save & Take Screenshots

1. Click **File** ➔ **Save As** ➔ Save to:
   ```
   c:\Users\SUMANJALI\Desktop\End-to-End E-Commerce Sales Analysis & Business Intelligence Dashboard\powerbi\ecommerce_dashboard.pbix
   ```
2. Press **Windows Key + Shift + S** to capture screenshots of each page:
   - Save them into: `screenshots/sales_overview.png`, `screenshots/product_analysis.png`, etc.
