import psycopg2

# Database connection details & sets up initial SQL database 

DATABASE_URL = (
    "postgresql://neondb_owner:npg_ngISkrv4PXx7@"
    "ep-green-grass-amgmprku-pooler.c-5.us-east-1.aws.neon.tech/"
    "neondb?sslmode=require&channel_binding=require"
)

def _get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS team4_flowers (
            flower_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            last_watered TIMESTAMP NOT NULL,
            water_level INT NOT NULL,
            min_water_required INT NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS team4_customers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS team4_orders (
            id SERIAL PRIMARY KEY,
            customer_id INT REFERENCES team4_customers(id),
            flower_id INT REFERENCES team4_flowers(flower_id),
            order_date DATE
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def seed_data():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO team4_flowers (name, last_watered, water_level, min_water_required)
        VALUES
            ('Rose', '2026-03-15', 20, 5),
            ('Tulip', '2026-03-15', 10, 7),
            ('Lily', '2024-03-15', 3, 5);
        
        INSERT INTO team4_customers (name, email)
        SELECT
            'Customer_' || g,
            'customer_' || g || '@example.com'
        FROM generate_series(1, 500) AS g;
                
        INSERT INTO team4_orders (customer_id, flower_id, order_date)
        SELECT
            (SELECT id FROM team4_customers ORDER BY random() LIMIT 1),
            (SELECT flower_id FROM team4_flowers ORDER BY random() LIMIT 1),
            CURRENT_DATE - ((random() * 365)::INT)
        FROM generate_series(1, 10000);
    """)
    conn.commit()
    cur.close()
    conn.close()