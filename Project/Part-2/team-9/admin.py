import psycopg2
from db_conn import DATABASE_URL

def _get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS team9_flowers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            last_watered DATE NOT NULL,
            last_watered_water_level INT NOT NULL,
            water_level INT NOT NULL,
            min_water_required INT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS team9_customers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100)
        );

        CREATE TABLE IF NOT EXISTS team9_orders (
            id SERIAL PRIMARY KEY,
            customer_id INT REFERENCES team9_customers(id),
            flower_id INT REFERENCES team9_flowers(id),
            order_date DATE
        );

        CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON team9_orders(customer_id);
        CREATE INDEX IF NOT EXISTS idx_orders_flower_id ON team9_orders(flower_id);
        CREATE INDEX IF NOT EXISTS idx_flowers_name ON team9_flowers(name);
    """)
    conn.commit()
    cur.close()
    conn.close()

def seed_data():
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM team9_flowers;")
    count = cur.fetchone()[0]
    
    if count == 0:
        cur.execute("""
            INSERT INTO team9_flowers (name, last_watered, water_level, last_watered_water_level, min_water_required) 
            VALUES 
            ('Rose', '2024-02-10', 20, 20, 5),
            ('Tulip', '2024-02-08', 10, 10, 7),
            ('Lily', '2024-02-05', 3, 3, 5);
        """)
        conn.commit()

    cur.execute("SELECT COUNT(*) FROM team9_customers;")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO team9_customers (name, email)
            SELECT
                'Customer_' || g,
                'customer_' || g || '@example.com'
            FROM generate_series(1, 500) AS g;
        """)
        conn.commit()

    cur.execute("SELECT COUNT(*) FROM team9_orders;")
    if cur.fetchone()[0] == 0:
        cur.execute("""
        INSERT INTO team9_orders (customer_id, flower_id, order_date)
        SELECT
            (random() * 499 + 1)::INT,
            (random() * 2 + 1)::INT,
            CURRENT_DATE - ((random() * 365)::INT)
        FROM generate_series(1, 10000);
        """)
        conn.commit()

    cur.close()
    conn.close()
    
def update_water_levels():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE team9_flowers
        SET water_level = GREATEST(last_watered_water_level - (5 * (CURRENT_DATE - last_watered)), 0);
    """)
    conn.commit()
    cur.close()
    conn.close()


