import psycopg2
from psycopg2.extras import execute_values

DATABASE_URL = (
    "postgresql://neondb_owner:npg_mCN6deqDx1iO@"
    "ep-square-lab-ambs03t1-pooler.c-5.us-east-1.aws.neon.tech/"
    "neondb?sslmode=require&channel_binding=require"
)

N_CUSTOMERS = 500
N_ORDERS = 10000

def _get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    """Create team3_flowers (Part 1) and team3_customers / team3_orders (Part 2)."""
    conn = _get_conn()
    cur = conn.cursor()

    # Part 1 table. Note: no DROP here because team3_orders has an FK to it.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS team3_flowers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            last_watered DATE NOT NULL,
            water_level INT NOT NULL,
            min_water_required INT NOT NULL,
            color VARCHAR(50) DEFAULT 'Mixed',
            price NUMERIC(10, 2) DEFAULT 0.00
        );
    """)

    # Part 2 tables.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS team3_customers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100)
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS team3_orders (
            id SERIAL PRIMARY KEY,
            customer_id INT REFERENCES team3_customers(id),
            flower_id INT REFERENCES team3_flowers(id),
            order_date DATE
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

def seed_data():
    """Seed flowers, customers, and orders. Idempotent."""
    conn = _get_conn()
    cur = conn.cursor()

    # Flowers (Part 1).
    cur.execute("""
        INSERT INTO team3_flowers (name, last_watered, water_level, min_water_required)
        VALUES
            ('Rose', '2026-03-10', 20, 5),
            ('Tulip', '2026-03-11', 10, 10),
            ('Lily', '2026-03-11', 15, 5)
        ON CONFLICT (name) DO NOTHING;
    """)

    # Customers (Part 2) — at most 500.
    cur.execute("SELECT COUNT(*) FROM team3_customers;")
    if cur.fetchone()[0] < N_CUSTOMERS:
        cur.execute(f"""
            INSERT INTO team3_customers (name, email)
            SELECT 'Customer_' || g, 'customer_' || g || '@example.com'
            FROM generate_series(1, {N_CUSTOMERS}) AS g;
        """)

    # Orders (Part 2) — at most 10,000. flower_id must reference a real row,
    # so pick from existing team3_flowers rather than a fixed range.
    cur.execute("SELECT COUNT(*) FROM team3_orders;")
    order_count = cur.fetchone()[0]
    if order_count < N_ORDERS:
        remaining = N_ORDERS - order_count
        cur.execute(f"""
            INSERT INTO team3_orders (customer_id, flower_id, order_date)
            SELECT
                (random() * ({N_CUSTOMERS} - 1) + 1)::INT,
                (SELECT id FROM team3_flowers ORDER BY random() LIMIT 1),
                CURRENT_DATE - ((random() * 365)::INT)
            FROM generate_series(1, {remaining});
        """)

    conn.commit()
    cur.close()
    conn.close()

def create_indexes():
    """Indexes used by the fast query. Safe to re-run."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON team3_orders(customer_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_flower_id ON team3_orders(flower_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_customers_name ON team3_customers(name);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_flowers_name ON team3_flowers(name);")
    conn.commit()
    cur.close()
    conn.close()

def update_water_levels():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE team3_flowers
        SET water_level = water_level - (5 * (CURRENT_DATE - last_watered));
    """)
    conn.commit()
    cur.close()
    conn.close()