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
    count = cur.fetchone()[0]

    if count == 0:
        cur.execute("""
            INSERT INTO team7_flowers (name, last_watered, water_level, min_water_required) 
            VALUES 
                ('Rose', '2024-02-10', 20, 5),
                ('Tulip', '2024-02-08', 10, 7),
                ('Lily', '2024-02-05', 3, 5);
        """)

    conn.commit()
    cur.close()
    conn.close()

