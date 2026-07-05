-- ============================================================
-- schema.sql
-- Creates the core tables for the retail analytics project.
-- Compatible with PostgreSQL (minor tweaks needed for MySQL/SQLite).
-- ============================================================

DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;

CREATE TABLE customers (
    customer_id     INTEGER PRIMARY KEY,
    country         VARCHAR(100)
);

CREATE TABLE products (
    stock_code      VARCHAR(20) PRIMARY KEY,
    description     VARCHAR(255),
    category        VARCHAR(100),
    unit_price      NUMERIC(10, 2)
);

CREATE TABLE transactions (
    invoice_no      BIGINT,
    stock_code      VARCHAR(20) REFERENCES products(stock_code),
    customer_id     INTEGER REFERENCES customers(customer_id),
    quantity        INTEGER,
    unit_price      NUMERIC(10, 2),
    invoice_date    TIMESTAMP,
    line_total      NUMERIC(12, 2),
    is_return       BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_transactions_customer ON transactions(customer_id);
CREATE INDEX idx_transactions_date ON transactions(invoice_date);
CREATE INDEX idx_transactions_stock ON transactions(stock_code);

-- Load cleaned CSVs into these tables using your DB client, e.g. (psql):
-- \copy customers FROM 'data/clean_customers.csv' DELIMITER ',' CSV HEADER;
-- \copy products FROM 'data/clean_products.csv' DELIMITER ',' CSV HEADER;
-- \copy transactions FROM 'data/clean_transactions.csv' DELIMITER ',' CSV HEADER;
