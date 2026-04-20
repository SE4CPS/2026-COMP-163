import psycopg2

DATABASE_URL = (
"postgresql://readonly:ReadOnly456%21@"
"ep-curly-bird-anqf0rre-pooler.c-6.us-east-1.aws.neon.tech/"
"neondb?sslmode=require&channel_binding=require"
)

def _get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
     CREATE TABLE IF NOT EXISTS team1_flowers (
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
    INSERT INTO team1_flowers(name, last_watered, water_level, min_water_required)
    VALUES
        ('Rose', '2023-01-01', 20, 5),
        ('Tulip', '2023-01-02', 10, 7),
        ('Lily', '2023-01-03', 3, 5)
    ON CONFLICT (name) DO NOTHING;
""")
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    init_db()
    seed_data()