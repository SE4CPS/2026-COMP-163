import psycopg2

# Neon PostgreSQL connection string
DATABASE_URL = (
    "postgresql://neondb_owner:npg_M5sVheSzQLv4@"
    "ep-shrill-tree-a819xf7v-pooler.eastus2.azure.neon.tech/"
    "neondb?sslmode=require"
)

try:
    # 1. Connect to PostgreSQL
    conn = psycopg2.connect(DATABASE_URL)
    print("Connected to PostgreSQL successfully.")

    # 2. Create cursor
    cur = conn.cursor()

    # 3. Create Furniture table (if it does not exist)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Furniture (
            furniture_id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL DEFAULT 'General',
            price NUMERIC(10,2) NOT NULL CHECK (price >= 0)
        );
    """)
    conn.commit()
    print("Furniture table ready.")

    # 4. Insert sample data
    cur.execute("""
        INSERT INTO Furniture (name, category, price)
        VALUES
            ('Chair', 'Seating', 39.99),
            ('Table', 'Surface', 129.00),
            ('Desk', 'Surface', 199.50)
        ON CONFLICT (name) DO NOTHING;
    """)
    conn.commit()
    print("Sample data inserted.")

    # 5. Query the table
    cur.execute("SELECT furniture_id, name, category, price FROM Furniture ORDER BY furniture_id;")
    rows = cur.fetchall()

    print("\nFurniture records:")
    for row in rows:
        print(row)

    # 6. Cleanup
    cur.close()
    conn.close()
    print("\nConnection closed.")

except Exception as e:
    print("Database error:", e)
