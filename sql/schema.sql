-- ==============================================================================
-- POSTGRESQL RELATIONAL SCHEMA: E-COMMERCE SALES ANALYSIS & BI
-- Star / Snowflake Schema Design with Primary & Foreign Key Constraints
-- ==============================================================================

-- Drop tables if existing (in reverse dependency order)
DROP TABLE IF EXISTS fact_order_reviews CASCADE;
DROP TABLE IF EXISTS fact_order_payments CASCADE;
DROP TABLE IF EXISTS fact_order_items CASCADE;
DROP TABLE IF EXISTS fact_orders CASCADE;
DROP TABLE IF EXISTS dim_sellers CASCADE;
DROP TABLE IF EXISTS dim_customers CASCADE;
DROP TABLE IF EXISTS dim_products CASCADE;
DROP TABLE IF EXISTS dim_geolocation CASCADE;

-- -----------------------------------------------------------------------------
-- 1. Geolocation Dimension
-- -----------------------------------------------------------------------------
CREATE TABLE dim_geolocation (
    zip_code_prefix VARCHAR(10) PRIMARY KEY,
    latitude NUMERIC(10, 6),
    longitude NUMERIC(10, 6),
    city VARCHAR(100),
    state VARCHAR(5)
);

-- -----------------------------------------------------------------------------
-- 2. Customers Dimension
-- -----------------------------------------------------------------------------
CREATE TABLE dim_customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50) NOT NULL,
    customer_zip_code_prefix VARCHAR(10),
    customer_city VARCHAR(100),
    customer_state VARCHAR(5)
);

CREATE INDEX idx_customers_unique_id ON dim_customers(customer_unique_id);
CREATE INDEX idx_customers_state ON dim_customers(customer_state);

-- -----------------------------------------------------------------------------
-- 3. Sellers Dimension
-- -----------------------------------------------------------------------------
CREATE TABLE dim_sellers (
    seller_id VARCHAR(50) PRIMARY KEY,
    seller_zip_code_prefix VARCHAR(10),
    seller_city VARCHAR(100),
    seller_state VARCHAR(5)
);

CREATE INDEX idx_sellers_state ON dim_sellers(seller_state);

-- -----------------------------------------------------------------------------
-- 4. Products Dimension
-- -----------------------------------------------------------------------------
CREATE TABLE dim_products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_name_lenght INT,
    product_description_lenght INT,
    product_photos_qty INT,
    product_weight_g NUMERIC(10, 2),
    product_length_cm NUMERIC(10, 2),
    product_height_cm NUMERIC(10, 2),
    product_width_cm NUMERIC(10, 2),
    product_category_name_english VARCHAR(100)
);

CREATE INDEX idx_products_category ON dim_products(product_category_name_english);

-- -----------------------------------------------------------------------------
-- 5. Orders Fact Table (Header / Order Level)
-- -----------------------------------------------------------------------------
CREATE TABLE fact_orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES dim_customers(customer_id),
    order_status VARCHAR(30),
    order_purchase_timestamp TIMESTAMP NOT NULL,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,
    order_year INT,
    order_month INT,
    order_year_month VARCHAR(7),
    order_day_of_week VARCHAR(15),
    delivery_duration_days NUMERIC(10, 2),
    estimated_vs_actual_days NUMERIC(10, 2),
    is_delayed INT
);

CREATE INDEX idx_orders_customer ON fact_orders(customer_id);
CREATE INDEX idx_orders_purchase_date ON fact_orders(order_purchase_timestamp);
CREATE INDEX idx_orders_status ON fact_orders(order_status);
CREATE INDEX idx_orders_year_month ON fact_orders(order_year_month);

-- -----------------------------------------------------------------------------
-- 6. Order Items Fact Table (Line Item Level)
-- -----------------------------------------------------------------------------
CREATE TABLE fact_order_items (
    order_id VARCHAR(50) REFERENCES fact_orders(order_id),
    order_item_id INT NOT NULL,
    product_id VARCHAR(50) REFERENCES dim_products(product_id),
    seller_id VARCHAR(50) REFERENCES dim_sellers(seller_id),
    shipping_limit_date TIMESTAMP,
    price NUMERIC(10, 2) NOT NULL,
    freight_value NUMERIC(10, 2) NOT NULL,
    total_item_value NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (order_id, order_item_id)
);

CREATE INDEX idx_order_items_product ON fact_order_items(product_id);
CREATE INDEX idx_order_items_seller ON fact_order_items(seller_id);

-- -----------------------------------------------------------------------------
-- 7. Order Payments Fact Table
-- -----------------------------------------------------------------------------
CREATE TABLE fact_order_payments (
    order_id VARCHAR(50) REFERENCES fact_orders(order_id),
    payment_sequential INT NOT NULL,
    payment_type VARCHAR(50) NOT NULL,
    payment_installments INT NOT NULL,
    payment_value NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (order_id, payment_sequential)
);

CREATE INDEX idx_payments_type ON fact_order_payments(payment_type);

-- -----------------------------------------------------------------------------
-- 8. Order Reviews Fact Table
-- -----------------------------------------------------------------------------
CREATE TABLE fact_order_reviews (
    review_id VARCHAR(50),
    order_id VARCHAR(50) REFERENCES fact_orders(order_id),
    review_score INT NOT NULL,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP,
    PRIMARY KEY (review_id, order_id)
);

CREATE INDEX idx_reviews_score ON fact_order_reviews(review_score);
