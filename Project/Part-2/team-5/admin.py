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
        CREATE TABLE IF NOT EXISTS team5_flowers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            last_watered DATE NOT NULL,
            water_level INT NOT NULL,
            min_water_required INT NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS team5_customers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100)
        );
                
        CREATE TABLE IF NOT EXISTS team5_orders (
            id SERIAL PRIMARY KEY,
            customer_id INT REFERENCES team5_customers(id),
            flower_id INT REFERENCES team5_flowers(id),
            order_date DATE
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def seed_data():
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM team5_flowers;")
    count = cur.fetchone()[0]

    if count == 0:
        cur.execute("""
            INSERT INTO team5_flowers (name, last_watered, water_level, min_water_required) 
                VALUES 
                    ('Rose', '2026-02-10', 20, 5), 
                    ('Tulip', '2026-03-08', 10, 7),
                    ('Lily', '2026-03-05', 3, 5),  
                    ('Daisy', '2026-03-01', 0, 3),
                    ('Chrysanthemum', '2026-03-19', 9, 10),
                    ('Orchid', '2026-03-20', 8, 8)
        """)

        cur.execute("""
            UPDATE team5_flowers 
            SET water_level = water_level - (5 * (CURRENT_DATE - last_watered))
            WHERE last_watered < CURRENT_DATE;
        """)
    conn.commit()
    cur.close()
    conn.close()