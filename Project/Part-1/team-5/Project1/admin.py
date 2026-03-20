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
    """)
    conn.commit()
    cur.close()
    conn.close()

def seed_data():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO team5_flowers (id, name, last_watered, water_level, min_water_required) 
            VALUES 
                (1, 'Rose', '2026-02-10', 20, 5), 
                (2, 'Tulip', '2026-03-08', 10, 7),
                (3, 'Lily', '2026-03-05', 3, 5),  
                (4, 'Daisy', '2026-03-01', 0, 3),
                (5, 'Chrysanthemum', '2026-03-19', 9, 10),
                (6, 'Orchid', '2026-03-20', 8, 8) ON CONFLICT (id) DO NOTHING;
        UPDATE team5_flowers
        SET water_level = water_level - (5 * (CURRENT_DATE - last_watered));
    """)
    conn.commit()
    cur.close()
    conn.close()