-- Team 2 Part 2 — indexes for optimized joins (run after tables exist).
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON team2_orders (customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_flower_id ON team2_orders (flower_id);
CREATE INDEX IF NOT EXISTS idx_flowers_name ON team2_flowers (name);
