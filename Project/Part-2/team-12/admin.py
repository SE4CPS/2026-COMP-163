import psycopg2

DATABASE_URL = (
    "postgresql://neondb_owner:npg_7Wbwi6IhVnou"
    "@ep-patient-silence-a4j19orv-pooler.us-east-1.aws.neon.tech"
    "/neondb?sslmode=require&channel_binding=require"
)

# Get database connection
def _get_conn():
    return psycopg2.connect(DATABASE_URL)

# Initialize database and create flowers table
def init_db():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        DROP TABLE IF EXISTS team12_flowers CASCADE;
        CREATE TABLE IF NOT EXISTS team12_flowers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            last_watered DATE NOT NULL,
            water_level INT NOT NULL,
            min_water_required INT NOT NULL
        );
                
        DROP TABLE IF EXISTS team12_customers CASCADE;
        CREATE TABLE IF NOT EXISTS team12_customers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL        
        );
                
        DROP TABLE IF EXISTS team12_orders CASCADE;
        CREATE TABLE IF NOT EXISTS team12_orders (
            id SERIAL PRIMARY KEY,
            customer_id INT REFERENCES team12_customers(id),
            flower_id INT REFERENCES team12_flowers(id),
            order_date DATE
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Initialize flower data
def seed_data():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO team12_flowers (name, 
                                    last_watered,
                                    water_level,
                                    min_water_required)
        VALUES
            ('Rose', '2024-02-10', 20, 5),
            ('Tulip', '2024-02-08', 10, 7),
            ('Lily', '2024-02-05', 3, 5)
        ON CONFLICT DO NOTHING;
                
        INSERT INTO team12_customers (name, email)
        SELECT
            'Customer_' || g,
            'customer_' || g || '@example.com'
        FROM generate_series(1, 500) AS g;
                
        INSERT INTO team12_orders (customer_id, flower_id, order_date)
        SELECT
            (random() * 499 + 1)::INT,
            (random() * 2 + 1)::INT,  -- adjust based on team12_flowers
            CURRENT_DATE - ((random() * 365)::INT)
        FROM generate_series(1, 10000);
    """)

    conn.commit()
    cur.close()
    conn.close()

def create_index():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON team12_orders(customer_id);
        CREATE INDEX IF NOT EXISTS idx_orders_flower_id   ON team12_orders(flower_id);
        CREATE INDEX IF NOT EXISTS idx_flowers_name       ON team12_flowers(name);
        CREATE INDEX IF NOT EXISTS idx_customers_name     ON team12_customers(name);
    """)
    conn.commit()
    cur.close()
    conn.close()