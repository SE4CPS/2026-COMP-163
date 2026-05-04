CREATE TABLE team13_customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE team13_orders (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES team13_customers(id),
    flower_id INT REFERENCES team13_flowers(id),
    order_date DATE
);

INSERT INTO team13_customers (name, email)
SELECT
    'Customer_' || g,
    'customer_' || g || '@example.com'
FROM generate_series(1, 500) AS g;

INSERT INTO team13_flowers (name, last_watered, water_level, min_water_required)
SELECT
    'Flower_' || g,
    CURRENT_DATE - ((random() * 30)::INT),
    (random() * 30 + 1)::INT,
    (random() * 10 + 1)::INT
FROM generate_series(1, 100) AS g;

INSERT INTO team13_orders (customer_id, flower_id, order_date)
SELECT
    (random() * 499 + 1)::INT,
    (random() * 99 + 1)::INT,
    CURRENT_DATE - ((random() * 365)::INT)
FROM generate_series(1, 10000);

CREATE INDEX idx_team13_orders_customer_id ON team13_orders(customer_id);
CREATE INDEX idx_team13_orders_flower_id ON team13_orders(flower_id);
CREATE INDEX idx_team13_flowers_name ON team13_flowers(name);
CREATE INDEX idx_team13_customers_name ON team13_customers(name);

-- Slow Query
SELECT *
FROM team13_orders o
JOIN team13_customers c ON o.customer_id = c.id
JOIN team13_flowers f ON o.flower_id = f.id
WHERE LOWER(c.name) LIKE '%customer%'
   OR LOWER(f.name) LIKE '%flower%'
ORDER BY LOWER(c.email), LOWER(f.name), o.order_date;

-- Fast Query
SELECT
    o.id,
    c.name AS customer_name,
    f.name AS flower_name,
    o.order_date
FROM team13_orders o
JOIN team13_customers c ON o.customer_id = c.id
JOIN team13_flowers f ON o.flower_id = f.id
WHERE c.name LIKE 'Customer_1%'
LIMIT 50;