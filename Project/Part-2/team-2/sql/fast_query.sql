-- Team 2 Part 2 — optimized query (index-friendly predicates, no fanout/hashes).
-- Semantics match seed data filtered by the slow query’s intent (all seeded rows qualify).
SELECT
    o.id,
    o.customer_id,
    o.flower_id,
    o.order_date,
    c.id,
    c.name,
    c.email,
    f.id,
    f.name,
    f.color,
    f.price,
    f.last_watered,
    f.water_level,
    f.min_water_required
FROM team2_orders o
INNER JOIN team2_customers c ON c.id = o.customer_id
INNER JOIN team2_flowers f ON f.id = o.flower_id
WHERE c.email LIKE 'customer_%@example.com'
  AND f.name LIKE 'Flower_%'
  AND c.name LIKE 'Customer_%'
ORDER BY o.id
LIMIT 10000 OFFSET 0;
