import psycopg2
import time

DATABASE_URL = (
    "postgresql://neondb_owner:npg_XUjioFP10Nyk@ep-empty-mud-anusqxyo-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)

def _get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS team7_flowers (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL DEFAULT 'Unknown',
        last_watered DATE NOT NULL,
        water_level INT NOT NULL CHECK (water_level >= 0),
        min_water_required INT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS team7_customers (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE
    );

    CREATE TABLE IF NOT EXISTS team7_orders (
        id SERIAL PRIMARY KEY,
        customer_id INT REFERENCES team7_customers(id),
        flower_id INT REFERENCES team7_flowers(id),
        order_date DATE NOT NULL DEFAULT CURRENT_DATE
    );
    """)

    conn.commit()
    cur.close()
    conn.close()

def seed_data():
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM team7_flowers;")
    flower_count = cur.fetchone()[0]

    if flower_count < 100:
        cur.execute("""
            INSERT INTO team7_flowers (name, last_watered, water_level, min_water_required)
            SELECT
                'Flower_' || g,
                CURRENT_DATE - ((random() * 30)::INT),
                (random() * 20)::INT,
                5 + (random() * 5)::INT
            FROM generate_series(%s, 100) AS g;
        """, (flower_count + 1,))

    cur.execute("SELECT COUNT(*) FROM team7_customers;")
    customer_count = cur.fetchone()[0]

    if customer_count < 500:
        cur.execute("""
            INSERT INTO team7_customers (name, email)
            SELECT
                'Customer_' || g,
                'customer_' || g || '@example.com'
            FROM generate_series(%s, 500) AS g
            ON CONFLICT (email) DO NOTHING;
        """, (customer_count + 1,))

    cur.execute("SELECT COUNT(*) FROM team7_orders;")
    order_count = cur.fetchone()[0]

    if order_count < 10000:
        rows_to_add = 10000 - order_count
        cur.execute("""
            INSERT INTO team7_orders (customer_id, flower_id, order_date)
            SELECT
                (random() * 499 + 1)::INT,
                (random() * 99 + 1)::INT,
                CURRENT_DATE - ((random() * 365)::INT)
            FROM generate_series(1, %s);
        """, (rows_to_add,))

    conn.commit()
    cur.close()
    conn.close()

def create_indexes():
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_orders_customer_id
            ON team7_orders(customer_id);

        CREATE INDEX IF NOT EXISTS idx_orders_flower_id
            ON team7_orders(flower_id);

        CREATE INDEX IF NOT EXISTS idx_flowers_name
            ON team7_flowers(name);

        CREATE INDEX IF NOT EXISTS idx_customers_name
            ON team7_customers(name);

        CREATE INDEX IF NOT EXISTS idx_orders_order_date
            ON team7_orders(order_date);
    """)

    conn.commit()
    cur.close()
    conn.close()

def drop_indexes():
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute("""
        DROP INDEX IF EXISTS idx_orders_customer_id;
        DROP INDEX IF EXISTS idx_orders_flower_id;
        DROP INDEX IF EXISTS idx_flowers_name;
        DROP INDEX IF EXISTS idx_customers_name;
        DROP INDEX IF EXISTS idx_orders_order_date;
    """)

    conn.commit()
    cur.close()
    conn.close()

SLOW_SQL = """
SELECT
    o.id,
    c.name AS customer_name,
    c.email,
    f.name AS flower_name,
    o.order_date,
    f.water_level,
    f.min_water_required
FROM team7_orders o
JOIN team7_customers c
    ON o.customer_id = c.id
JOIN team7_flowers f
    ON o.flower_id = f.id
CROSS JOIN LATERAL generate_series(1, 4000) gs
WHERE LOWER(c.name) LIKE 'customer_%'
  AND LOWER(f.name) LIKE '%flower%'
ORDER BY LOWER(c.name), LOWER(f.name), o.order_date DESC
LIMIT 100 OFFSET 0;
"""

FAST_SQL = """
SELECT
    o.id,
    c.name AS customer_name,
    c.email,
    f.name AS flower_name,
    o.order_date,
    f.water_level,
    f.min_water_required
FROM team7_orders o
JOIN team7_customers c
    ON o.customer_id = c.id
JOIN team7_flowers f
    ON o.flower_id = f.id
WHERE c.name LIKE 'Customer_%'
  AND f.name LIKE 'Flower_%'
ORDER BY c.name, f.name, o.order_date DESC
LIMIT 25 OFFSET 0;
"""

def slow_query():
    conn = _get_conn()
    cur = conn.cursor()

    drop_indexes()

    start = time.time()
    cur.execute(SLOW_SQL)
    cur.fetchall()
    elapsed = time.time() - start

    cur.close()
    conn.close()

    return {
        "mode": "slow",
        "sql": SLOW_SQL.strip(),
        "elapsed_seconds": round(elapsed, 4)
    }

def fast_query():
    conn = _get_conn()
    cur = conn.cursor()

    sql = """
        SELECT
            o.id,
            c.name AS customer_name,
            c.email,
            f.name AS flower_name,
            o.order_date,
            f.water_level,
            f.min_water_required
        FROM team7_orders o
        JOIN team7_customers c
            ON o.customer_id = c.id
        JOIN team7_flowers f
            ON o.flower_id = f.id
        WHERE c.name LIKE 'Customer_%'
          AND f.name LIKE 'Flower_%'
        ORDER BY c.name, f.name, o.order_date DESC
        LIMIT 100;
    """

    start = time.time()
    cur.execute(sql)
    cur.fetchall()
    elapsed = time.time() - start

    cur.close()
    conn.close()

    return {
        "mode": "fast",
        "sql": sql,
        "elapsed_seconds": round(elapsed, 4)
    }
