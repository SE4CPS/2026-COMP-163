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
        CREATE TABLE IF NOT EXISTS team3_flowers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
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
        INSERT INTO team3_flowers (name, last_watered, water_level, min_water_required)
        VALUES
            ('Rose', '2026-03-10', 20, 5),
            ('Tulip', '2026-03-11', 10, 10),
            ('Lily', '2026-03-11', 15, 5)
        ON CONFLICT (name) DO NOTHING;
    """)
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