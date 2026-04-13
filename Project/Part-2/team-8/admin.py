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
    cur.execute("""
        CREATE TABLE IF NOT EXISTS team8_flowers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            last_watered DATE NOT NULL CHECK(last_watered <= CURRENT_DATE),
            water_level INT NOT NULL CHECK(water_level >= 0),
            min_water_required INT NOT NULL CHECK(min_water_required >= 0)
        );
        CREATE TABLE IF NOT EXISTS team8_customers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100)
        );
        CREATE TABLE IF NOT EXISTS team8_orders (
            id SERIAL PRIMARY KEY,
            customer_id INT REFERENCES team8_customers(id),
            flower_id INT REFERENCES team8_flowers(id),
            order_date DATE
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def seed_data():
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM team8_orders;")
    count = cur.fetchone()[0]


    if count == 0:
        cur.execute("""
            INSERT INTO team8_flowers (name, last_watered, water_level, min_water_required)
            VALUES
                ('Rose', '2026-03-09', 20, 5),
                ('Tulip', '2026-03-07', 10, 7),
                ('Lily', '2026-03-04', 3, 5),
                ('Azalea', '2026-03-14', 7, 10),
                ('Poppy', '2026-04-10', 35, 15)
            ON CONFLICT (name) DO NOTHING;
            
            INSERT INTO team8_customers (name, email)
            SELECT 
                'Customer_' || g, 
                'customer_' || g || '@gmail.com'
            FROM generate_series(1, 500) AS g;

            INSERT INTO team8_orders (customer_id, flower_id, order_date)
            SELECT
                (SELECT id FROM team8_customers ORDER BY random() LIMIT 1),
                (SELECT id FROM team8_flowers ORDER BY random() LIMIT 1),
                CURRENT_DATE - ((random() * 365)::INT)
            FROM generate_series(1, 10000);
        """) # Adjust line 65 based on team8_flowers
        conn.commit()
    
    cur.close()
    conn.close()