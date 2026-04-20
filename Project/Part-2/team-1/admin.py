import psycopg2

DATABASE_URL = (
"postgresql://neondb_owner:npg_XGW8VMqI4ohn@ep-red-snow-am3ghme3.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require"
)

def _get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
    DROP TABLE IF EXISTS team1_orders;
    DROP TABLE IF EXISTS team1_customers;
    DROP TABLE IF EXISTS team1_flowers;

    CREATE TABLE IF NOT EXISTS team1_flowers (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        last_watered DATE NOT NULL,
        water_level INT NOT NULL,
        min_water_required INT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS team1_customers (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS team1_orders (
        id SERIAL PRIMARY KEY,
        customer_id INT NOT NULL REFERENCES team1_customers(id),
        flower_id INT NOT NULL REFERENCES team1_flowers(id),
        order_date DATE NOT NULL DEFAULT CURRENT_DATE
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
        ('Lily', '2023-01-03', 3, 5);

    INSERT INTO team1_customers(name)
    VALUES
        ('Alice'),
        ('Bob'),
        ('Carol');

    INSERT INTO team1_orders(customer_id, flower_id, order_date)
    VALUES
        (1, 1, '2023-02-01'),
        (2, 1, '2023-02-02'),
        (3, 2, '2023-02-03'),
        (1, 3, '2023-02-04');
    """)
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    init_db()
    seed_data()