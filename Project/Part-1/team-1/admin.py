import psycopg2
import time

DATABASE_URL = (
    "postgresql://neondb_owner:npg_M5sVheSzQLv4@"
    "ep-shrill-tree-a819xf7v-pooler.eastus2.azure.neon.tech/"
    "neondb?sslmode=require"
)

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS team1_flowers (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL,
        last_watered DATE NOT NULL,
        water_level INT NOT NULL,
        min_water_required INT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS team1_customers (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) UNIQUE,
        email VARCHAR(100)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS team1_orders (
        id SERIAL PRIMARY KEY,
        customer_id INT REFERENCES team1_customers(id),
        flower_id INT REFERENCES team1_flowers(id),
        order_date DATE
    );
    """)

    conn.commit()
    cur.close()
    conn.close()

def seed_data():
    conn = get_conn()
    cur = conn.cursor()

    print("Seeding data... (this may take a while)")

    # Flowers
    cur.execute("""
    INSERT INTO team1_flowers(name, last_watered, water_level, min_water_required)
    VALUES
        ('Rose', CURRENT_DATE, 20, 5),
        ('Tulip', CURRENT_DATE, 10, 7),
        ('Lily', CURRENT_DATE, 3, 5)
    ON CONFLICT (name) DO NOTHING;
    """)

    cur.execute("""
    INSERT INTO team1_customers (name, email)
    SELECT
        'Customer_' || g,
        'customer_' || g || '@example.com'
    FROM generate_series(1, 50000) AS g
    ON CONFLICT (name) DO NOTHING;
    """)

    cur.execute("""
    INSERT INTO team1_orders (customer_id, flower_id, order_date)
    SELECT
        c.id,
        f.id,
        CURRENT_DATE - ((random() * 365)::INT)
    FROM generate_series(1, 300000) g
    JOIN LATERAL (
        SELECT id FROM team1_customers ORDER BY RANDOM() LIMIT 1
    ) c ON TRUE
    JOIN LATERAL (
        SELECT id FROM team1_flowers ORDER BY RANDOM() LIMIT 1
    ) f ON TRUE;
    """)

    conn.commit()
    cur.close()
    conn.close()

    print("Seeding complete.\n")

def run_expensive_query():
    conn = get_conn()
    cur = conn.cursor()

    print("Running VERY slow query... ")

    query = """
    SELECT *
    FROM team1_orders o
    JOIN team1_customers c
        ON LOWER(c.id::text) = LOWER(o.customer_id::text)
    JOIN team1_flowers f
        ON UPPER(f.id::text) = UPPER(o.flower_id::text)

    -- Artificial slowdown
    JOIN generate_series(1,3) g ON TRUE

    WHERE 
        LOWER(c.name) LIKE '%a%' OR
        UPPER(f.name) LIKE '%B%' OR
        encode(digest(c.email, 'sha256'), 'hex') LIKE '%a%'

    ORDER BY 
        LENGTH(LOWER(c.name)),
        LENGTH(UPPER(f.name)),
        RANDOM(),
        o.order_date DESC;
    """

    start = time.time()

    cur.execute(query)

    print("Query executed. Fetching sample rows...\n")

    count = 0
    for row in cur:
        print(row)
        count += 1
        if count >= 5:
            break

    end = time.time()

    print(f"\nQuery took: {end - start:.2f} seconds\n")

    cur.close()
    conn.close()

def run_optimized_query():
    conn = get_conn()
    cur = conn.cursor()

    print("Running OPTIMIZED query... ⚡")

    query = """
    SELECT * FROM (
      (
          SELECT 
            o.id,
            c.name,
            c.email,
            f.name AS flower_name,
            o.order_date
        FROM team1_orders o
        JOIN team1_customers c 
            ON o.customer_id = c.id
        JOIN team1_flowers f 
            ON o.flower_id = f.id
        WHERE c.name LIKE 'Customer_1%'
        LIMIT 50
      )
        UNION
      (
        SELECT 
            o.id,
            c.name,
            c.email,
            f.name AS flower_name,
            o.order_date
        FROM team1_orders o
        JOIN team1_customers c 
            ON o.customer_id = c.id
        JOIN team1_flowers f 
            ON o.flower_id = f.id
        WHERE f.name = 'Rose'
        LIMIT 50
        )
    ) sub
    ORDER BY order_date DESC
    LIMIT 50 OFFSET 0;
    """

    start = time.time()

    cur.execute(query)
    rows = cur.fetchall()

    end = time.time()

    print(f"Optimized query took: {end - start:.4f} seconds")
    print(f"Rows returned: {len(rows)}\n")

    for row in rows[:5]:
        print(row)

    cur.close()
    conn.close()

if __name__ == "__main__":
    init_db()
    seed_data()
    print("after INDEXES")
    run_optimized_query()

    print("BEFORE INDEXES")
    run_expensive_query()

