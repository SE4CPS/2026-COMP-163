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
        CREATE TABLE team5_flowers (
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
        INSERT INTO team5_flowers (name, last_watered, water_level, min_water_required) 
            VALUES 
                ('Rose', '2024-02-10', 20, 5),
                ('Tulip', '2024-02-08', 10, 7),
                ('Lily', '2024-02-05', 3, 5);
        ON CONFLICT (name) DO NOTHING;
    """)
    conn.commit()
    cur.close()
    conn.close()