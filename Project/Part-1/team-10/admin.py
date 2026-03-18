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
        CREATE TABLE IF NOT EXISTS Flower (
            flower_id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            color TEXT NOT NULL DEFAULT 'Mixed',
            price NUMERIC(10,2) NOT NULL CHECK (price >= 0)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def seed_data():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Flower (name, color, price)
        VALUES
            ('Rose', 'Red', 4.99),
            ('Tulip', 'Yellow', 3.50),
            ('Lily', 'White', 5.25)
        ON CONFLICT (name) DO NOTHING;
    """)
    conn.commit()
    cur.close()
    conn.close()