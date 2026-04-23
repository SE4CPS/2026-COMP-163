import psycopg2

DATABASE_URL = (
    "postgresql://neondb_owner:npg_b64dzjqCkBiF@"
    "ep-soft-king-anuhub9k-pooler.c-6.us-east-1.aws.neon.tech/"
    "neondb?sslmode=require&channel_binding=require"
)

def _get_conn():
    return psycopg2.connect(DATABASE_URL)

def select_flower(id=None):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        if id is None:
            cur.execute("SELECT id, name FROM team10_flowers ORDER BY id;")
            rows = cur.fetchall()
            return [{"id": r[0], "name": r[1]} for r in rows]
        else:
            cur.execute("SELECT id, name FROM team10_flowers WHERE id = %s;", (id,))
            row = cur.fetchone()
            if not row:
                return None
            return {"id": row[0], "name": row[1]}
    finally:
        cur.close()
        conn.close()

def select_customer(id=None):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        if id is None:
            cur.execute("SELECT id, name, email FROM team10_customers ORDER BY id;")
            rows = cur.fetchall()
            return [{"id": r[0], "name": r[1], "email": r[2]} for r in rows]
        else:
            cur.execute("SELECT id, name, email FROM team10_customers WHERE id = %s;", (id,))
            row = cur.fetchone()
            if not row:
                return None
            return {"id": row[0], "name": row[1], "email": row[2]}
    finally:
        cur.close()
        conn.close()

def select_order(id=None):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        if id is None:
            cur.execute("SELECT id, customer_id, flower_id, order_date FROM team10_orders ORDER BY id;")
            rows = cur.fetchall()
            return [{"id": r[0], "customer_id": r[1], "flower_id": r[2], "order_date": r[3].strftime("%Y-%m-%d")} for r in rows]
        else:
            cur.execute("SELECT id, customer_id, flower_id, order_date FROM team10_orders WHERE id = %s;", (id,))
            row = cur.fetchone()
            if not row:
                return None
            return {"id": row[0], "customer_id": row[1], "flower_id": row[2], "order_date": row[3].strftime("%Y-%m-%d")}
    finally:
        cur.close()
        conn.close()

def select_order_with_details(id=None):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        if id is None:
            cur.execute("""
                SELECT o.id, o.customer_id, c.name, c.email, o.flower_id, f.name, o.order_date
                FROM team10_orders o
                JOIN team10_customers c ON o.customer_id = c.id
                JOIN team10_flowers f ON o.flower_id = f.id
                ORDER BY o.id;
            """)
            rows = cur.fetchall()
            return [{
                "order_id": r[0],
                "customer_id": r[1],
                "customer_name": r[2],
                "customer_email": r[3],
                "flower_id": r[4],
                "flower_name": r[5],
                "order_date": r[6].strftime("%Y-%m-%d")
            } for r in rows]
        else:
            cur.execute("""
                SELECT o.id, o.customer_id, c.name, c.email, o.flower_id, f.name, o.order_date
                FROM team10_orders o
                JOIN team10_customers c ON o.customer_id = c.id
                JOIN team10_flowers f ON o.flower_id = f.id
                WHERE o.id = %s;
            """, (id,))
            row = cur.fetchone()
            if not row:
                return None
            return {
                "order_id": row[0],
                "customer_id": row[1],
                "customer_name": row[2],
                "customer_email": row[3],
                "flower_id": row[4],
                "flower_name": row[5],
                "order_date": row[6].strftime("%Y-%m-%d")
            }
    finally:
        cur.close()
        conn.close()

def slow():
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            EXPLAIN ANALYZE
SELECT COUNT(*), COUNT(c.name), COUNT(f.name) FROM team10_orders o 
FULL JOIN team10_customers c ON 1=1
FULL JOIN team10_flowers  f ON 1=1
GROUP BY c.name, f.name
ORDER BY RANDOM();

        """)
        rows = cur.fetchall()
        result = [{"plan": str(r[0]) if r else ""} for r in rows]
        total_time = next((r["plan"] for r in result if "Execution Time" in r["plan"]), None)
        return total_time
    finally:
        cur.close()
        conn.close()

def fast():
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON team10_orders(customer_id);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_orders_flower_id ON team10_orders(flower_id);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_flowers_name ON team10_flowers(name);
        """)
        cur.execute("""
            EXPLAIN ANALYZE
SELECT
  c.id           AS customer_id,
  c.name         AS customer_name,
  f.id           AS flower_id,
  f.name         AS flower_name,
  COUNT(*)       AS purchases,
  MIN(o.order_date) AS first_order,
  MAX(o.order_date) AS last_order
FROM team10_orders o
JOIN team10_customers c ON o.customer_id = c.id
JOIN team10_flowers  f ON o.flower_id   = f.id
GROUP BY c.id, c.name, f.id, f.name
ORDER BY purchases DESC;



        """)
        rows = cur.fetchall()
        result = [{"plan": str(r[0]) if r else ""} for r in rows]
        total_time = next((r["plan"] for r in result if "Execution Time" in r["plan"]), None)
        return total_time
    finally:
        cur.close()
        conn.close()