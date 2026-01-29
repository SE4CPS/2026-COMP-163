-- ============================================
-- SQLite query performance demo (REAL timing)
-- ============================================

.timer on

PRAGMA journal_mode = OFF;
PRAGMA synchronous = OFF;
PRAGMA temp_store = MEMORY;

DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS orders;

-- --------------------------------------------
-- Tables
-- --------------------------------------------

CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  region      TEXT NOT NULL
);

CREATE TABLE orders (
  order_id    INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL,
  amount      INTEGER NOT NULL
);

-- --------------------------------------------
-- Data
-- Customers: 200,000 (1% = 'West')
-- Orders:    2,000,000
-- --------------------------------------------

WITH RECURSIVE seq(x) AS (
  SELECT 1
  UNION ALL
  SELECT x + 1 FROM seq WHERE x < 200000
)
INSERT INTO customers
SELECT
  x,
  CASE WHEN x % 100 = 0 THEN 'West' ELSE 'Other' END
FROM seq;

WITH RECURSIVE seq(x) AS (
  SELECT 1
  UNION ALL
  SELECT x + 1 FROM seq WHERE x < 2000000
)
INSERT INTO orders
SELECT
  x,
  (x % 200000) + 1,
  (x % 1000) + 1
FROM seq;

ANALYZE;

-- --------------------------------------------
-- SLOW QUERY
-- Forces bad join order (orders first)
-- --------------------------------------------

SELECT COUNT(*)
FROM orders o
CROSS JOIN customers c
WHERE o.customer_id = c.customer_id
  AND c.region = 'West'
  AND o.amount > 900;
