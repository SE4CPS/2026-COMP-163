import psycopg2

DATABASE_URL = (
    "postgresql://neondb_owner:npg_M5sVheSzQLv4@"
    "ep-shrill-tree-a819xf7v-pooler.eastus2.azure.neon.tech/"
    "neondb?sslmode=require"
)

def _get_conn():
    return psycopg2.connect(DATABASE_URL)   

def init_db():
    conn = _get_conn()
    cur = conn.cursor()
    # cur.execute("DROP TABLE IF EXISTS team11_flowers;") -- applies new constraints if changes made
    cur.execute("""
        CREATE TABLE IF NOT EXISTS team11_flowers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            last_watered DATE NOT NULL,
            water_level INT NOT NULL,
            min_water_required INT NOT NULL
        );
    """)

    # cur.execute("DROP TABLE IF EXISTS team11_customers;") -- applies new constraints if changes made
    cur.execute("""
        CREATE TABLE IF NOT EXISTS team11_customers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100)
        );
    """)

    # cur.execute("DROP TABLE IF EXISTS team11_orders;") -- applies new constraints if changes made
    cur.execute("""
        CREATE TABLE IF NOT EXISTS team11_orders (
            id SERIAL PRIMARY KEY,
            customer_id INT REFERENCES team11_customers(id),
            flower_id INT REFERENCES team11_flowers(id),
            order_date DATE
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

def seed_data():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO team11_flowers (name, last_watered, water_level, min_water_required) 
        VALUES 
            ('Rose', '2024-02-10', 20, 5),
            ('Tulip', '2024-02-08', 10, 7),
            ('Lily', '2026-03-17', 3, 5)
                ON CONFLICT (name) DO NOTHING;
    """)
    conn.commit()
    cur.close()
    conn.close()

def customer_data():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO team11_customers (name, email)
        SELECT 
                'Customer_' || g,
                'customer_' || g || '@example.com'
        FROM generate_series(1, 500) AS g;
    """)
    conn.commit()
    cur.close()
    conn.close()

def order_data():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO team11_orders (customer_id, flower_id, order_date)
        SELECT
            (random() * 499 + 1)::INT,
            (random() * 2 + 1)::INT,  -- adjust based on teamX_flowers
            CURRENT_DATE - ((random() * 365)::INT)
        FROM generate_series(1, 10000);
    """)
    conn.commit()
    cur.close()
    conn.close()

def all_data():
    seed_data()
    customer_data()
    order_data()

def print_customers(limit=20):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM team11_customers LIMIT %s;", (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    print(f"{'ID':<6} {'Name':<20} {'Email'}")
    print("-" * 50)
    for row in rows:
        print(f"{row[0]:<6} {row[1]:<20} {row[2]}")


def print_orders(limit=20):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT o.id, c.name, f.name, o.order_date
        FROM team11_orders o
        JOIN team11_customers c ON o.customer_id = c.id
        JOIN team11_flowers   f ON o.flower_id   = f.id
        ORDER BY o.order_date DESC
        LIMIT %s;
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    print(f"{'Order ID':<10} {'Customer':<20} {'Flower':<15} {'Date'}")
    print("-" * 60)
    for row in rows:
        print(f"{row[0]:<10} {row[1]:<20} {row[2]:<15} {row[3]}")