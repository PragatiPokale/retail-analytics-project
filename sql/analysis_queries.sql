-- ============================================================
-- analysis_queries.sql
-- Core business-question queries for the retail analytics project.
-- Run these against the tables created in schema.sql.
-- ============================================================

-- 1. MONTHLY REVENUE TREND
SELECT
    DATE_TRUNC('month', invoice_date) AS month,
    ROUND(SUM(line_total)::numeric, 2) AS revenue,
    COUNT(DISTINCT invoice_no) AS num_orders,
    COUNT(DISTINCT customer_id) AS active_customers
FROM transactions
WHERE is_return = FALSE
GROUP BY 1
ORDER BY 1;

-- 2. REVENUE BY COUNTRY
SELECT
    c.country,
    ROUND(SUM(t.line_total)::numeric, 2) AS revenue,
    COUNT(DISTINCT t.customer_id) AS num_customers
FROM transactions t
JOIN customers c ON c.customer_id = t.customer_id
WHERE t.is_return = FALSE
GROUP BY c.country
ORDER BY revenue DESC;

-- 3. TOP 10 PRODUCTS BY REVENUE
SELECT
    p.stock_code,
    p.description,
    p.category,
    ROUND(SUM(t.line_total)::numeric, 2) AS revenue,
    SUM(t.quantity) AS units_sold
FROM transactions t
JOIN products p ON p.stock_code = t.stock_code
WHERE t.is_return = FALSE
GROUP BY p.stock_code, p.description, p.category
ORDER BY revenue DESC
LIMIT 10;

-- 4. RFM BASE TABLE (Recency, Frequency, Monetary per customer)
-- Recency = days since last purchase, relative to the most recent date in the dataset
WITH last_date AS (
    SELECT MAX(invoice_date) AS max_date FROM transactions
)
SELECT
    t.customer_id,
    (SELECT max_date FROM last_date)::date - MAX(t.invoice_date)::date AS recency_days,
    COUNT(DISTINCT t.invoice_no) AS frequency,
    ROUND(SUM(t.line_total)::numeric, 2) AS monetary
FROM transactions t
WHERE t.is_return = FALSE AND t.customer_id IS NOT NULL
GROUP BY t.customer_id
ORDER BY monetary DESC;

-- 5. COHORT RETENTION (customers grouped by first purchase month)
WITH first_purchase AS (
    SELECT customer_id, DATE_TRUNC('month', MIN(invoice_date)) AS cohort_month
    FROM transactions
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
),
activity AS (
    SELECT
        t.customer_id,
        fp.cohort_month,
        DATE_TRUNC('month', t.invoice_date) AS activity_month
    FROM transactions t
    JOIN first_purchase fp ON fp.customer_id = t.customer_id
)
SELECT
    cohort_month,
    activity_month,
    (EXTRACT(YEAR FROM activity_month) - EXTRACT(YEAR FROM cohort_month)) * 12
        + (EXTRACT(MONTH FROM activity_month) - EXTRACT(MONTH FROM cohort_month)) AS month_index,
    COUNT(DISTINCT customer_id) AS active_customers
FROM activity
GROUP BY cohort_month, activity_month
ORDER BY cohort_month, activity_month;

-- 6. CHURN RISK FLAG (no purchase in the last 90 days relative to dataset max date)
WITH last_date AS (
    SELECT MAX(invoice_date) AS max_date FROM transactions
)
SELECT
    customer_id,
    MAX(invoice_date) AS last_purchase_date,
    (SELECT max_date FROM last_date)::date - MAX(invoice_date)::date AS days_since_last_purchase,
    CASE
        WHEN (SELECT max_date FROM last_date)::date - MAX(invoice_date)::date > 90 THEN 'At Risk'
        ELSE 'Active'
    END AS churn_status
FROM transactions
WHERE customer_id IS NOT NULL
GROUP BY customer_id
ORDER BY days_since_last_purchase DESC;
