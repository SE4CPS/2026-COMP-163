import os
import psycopg2

# UPDATED: Now points to your specific Neon instance by default
_DEFAULT_DATABASE_URL = (
    "postgresql://neondb_owner:npg_XGW8VMqI4ohn@"
    "ep-red-snow-am3ghme3-pooler.c-5.us-east-1.aws.neon.tech/"
    "neondb?sslmode=require&channel_binding=require"
)


def get_database_url():
    """
    Use DATABASE_URL from the environment only when it is non-empty.
    (If the var exists but is '', os.environ.get would otherwise skip the default.)
    """
    raw = os.environ.get("DATABASE_URL", "").strip()
    return raw if raw else _DEFAULT_DATABASE_URL


def _get_conn():
    return psycopg2.connect(get_database_url())


def init_db():
    """Create flowers (if missing), customers, and orders tables."""
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS team2_flowers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                color VARCHAR(50) NOT NULL DEFAULT 'Mixed',
                price NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
                last_watered DATE NOT NULL,
                water_level INT NOT NULL,
                min_water_required INT NOT NULL
            );
            """
        )
        cur.execute("DROP TABLE IF EXISTS team2_orders CASCADE;")
        cur.execute("DROP TABLE IF EXISTS team2_customers CASCADE;")
        cur.execute(
            """
            CREATE TABLE team2_customers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100)
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE team2_orders (
                id SERIAL PRIMARY KEY,
                customer_id INT REFERENCES team2_customers(id),
                flower_id INT REFERENCES team2_flowers(id),
                order_date DATE
            );
            """
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_orders_customer_id "
            "ON team2_orders (customer_id);"
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_orders_flower_id "
            "ON team2_orders (flower_id);"
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_flowers_name "
            "ON team2_flowers (name);"
        )
        conn.commit()
        print("Part 2 tables ready (team2_customers, team2_orders).")
    except Exception as e:
        conn.rollback()
        print("init_db error:", e)
        raise
    finally:
        cur.close()
        conn.close()


def seed_data():
    """At most 500 customers and 10_000 orders; 100 flowers for FK spread."""
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "TRUNCATE TABLE team2_orders, team2_customers, team2_flowers "
            "RESTART IDENTITY CASCADE;"
        )
        cur.execute(
            """
            INSERT INTO team2_flowers
                (name, color, price, last_watered, water_level, min_water_required)
            SELECT
                'Flower_' || g,
                CASE WHEN g % 2 = 0 THEN 'Mixed' ELSE 'Earth' END,
                (random() * 20 + 1)::NUMERIC(10,2),
                CURRENT_DATE - (g % 120),
                10,
                5
            FROM generate_series(1, 100) AS g;
            """
        )
        cur.execute(
            """
            INSERT INTO team2_customers (name, email)
            SELECT
                'Customer_' || g,
                'customer_' || g || '@example.com'
            FROM generate_series(1, 500) AS g;
            """
        )
        cur.execute(
            """
            INSERT INTO team2_orders (customer_id, flower_id, order_date)
            SELECT
                (floor(random() * 500) + 1)::INT,
                (floor(random() * 100) + 1)::INT,
                CURRENT_DATE - ((random() * 365)::INT)::INT
            FROM generate_series(1, 10000) AS g;
            """
        )
        cur.execute("ANALYZE team2_flowers;")
        cur.execute("ANALYZE team2_customers;")
        cur.execute("ANALYZE team2_orders;")
        conn.commit()
        print("Seeded team2_flowers (100), team2_customers (500), team2_orders (10000).")
    except Exception as e:
        conn.rollback()
        print("seed_data error:", e)
        raise
    finally:
        cur.close()
        conn.close()