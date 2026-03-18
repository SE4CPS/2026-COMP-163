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
        CREATE TABLE IF NOT EXISTS team2_flowers (
  id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(50) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    last_watered DATE NOT NULL,
    water_level INT NOT NULL,
    min_water_required INT NOT NULL
    );
    """)
    conn.commit()
    cur.close()
    conn.close()

def seed_data():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO team2_flowers (name, color, price, last_watered, water_level, min_water_required) 
VALUES 
('Rose', 'Red', 4.99, '2024-02-10', 20, 5),
('Tulip', 'Yellow', 3.50, '2024-02-08', 10, 7),
('Lily', 'White', 5.25, '2024-02-05', 3, 5);
    """)
    conn.commit()
    cur.close()
    conn.close()
