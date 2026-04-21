import psycopg2
from datetime import date
import time

DATABASE_URL = (
    "postgresql://neondb_owner:npg_kasM4eQ9VOzL@"
    "ep-lucky-cherry-anpfkxkt-pooler.c-6.us-east-1.aws.neon.tech/"
    "neondb?sslmode=require&channel_binding=require"
)

def _get_conn():
    return psycopg2.connect(DATABASE_URL)

def insert_flower(name, last_watered, water_level, min_water_required):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        sql = f"""
            INSERT INTO team11_flowers (name, last_watered, water_level, min_water_required)
            VALUES ('{name}', '{last_watered}', {water_level}, {min_water_required})
            ON CONFLICT (name) DO NOTHING;
        """
        cur.execute(sql)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Insert error:", e)
        return False
    finally:
        cur.close()
        conn.close()

def select_flower(id=None):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        if id is None:
            update_sql = """
                UPDATE team11_flowers
                SET water_level = GREATEST(
                    0,
                    water_level - (5 * (%s::date - last_watered))
            );
            """
            cur.execute(update_sql, (date.today(),))
            conn.commit()

            select_sql = """
                SELECT id, name, last_watered, water_level, min_water_required
                FROM team11_flowers
                ORDER BY id;
            """
            cur.execute(select_sql)
            rows = cur.fetchall()
            return [
                {
                    "id": r[0], 
                    "name": r[1],
                    "last_watered": r[2],
                    "water_level": r[3],
                    "min_water_required": r[4],
                }
                for r in rows
            ]
        else:
            sql = f"""
                SELECT *
                FROM team11_flowers
                WHERE id = {id};
            """
            cur.execute(sql)
            row = cur.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "name": row[1],
                "last_watered": row[2],
                "water_level": row[3],
                "min_water_required": row[4],
            }
    finally:
        cur.close()
        conn.close()

def update_flower(id, name, last_watered, water_level, min_water_required):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        sql = f"""
            UPDATE team11_flowers
            SET name = '{name}',
                last_watered = '{last_watered}',
                water_level = {water_level},
                min_water_required = {min_water_required}
            WHERE id = {id};
        """
        cur.execute(sql)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Update error:", e)
        return False
    finally:
        cur.close()
        conn.close()

def delete_flower(id):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        sql = f"""
            DELETE FROM team11_flowers
            WHERE id = {id};
        """
        cur.execute(sql)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Delete error:", e)
        return False
    finally:
        cur.close()
        conn.close()

def water_flower(id):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        sql = f"""
            UPDATE team11_flowers
            SET water_level = water_level + min_water_required,
                last_watered = CURRENT_DATE
            WHERE id = {id};
        """
        cur.execute(sql)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Watering error:", e)
        return False
    finally:
        cur.close()
        conn.close()

SLOW_SQL = """
SELECT
    o.id,
    o.customer_id,
    o.flower_id,
    o.order_date,
    c.id,
    c.name,
    c.email,
    f.id,
    f.name,
    f.last_watered,
    f.water_level,
    f.min_water_required,
    md5(LOWER(c.email) || LOWER(c.name)) AS encrypted_email,
    md5(LOWER(c.name) || LOWER(f.name) || CAST(o.order_date AS TEXT)) AS row_hash
FROM team11_orders o
JOIN team11_customers c ON o.customer_id = c.id
JOIN team11_flowers f ON o.flower_id = f.id
WHERE LOWER(c.name) LIKE '%customer%'
ORDER BY md5(LOWER(c.name) || LOWER(f.name) || LOWER(c.email)),
         md5(LOWER(c.email) || CAST(o.order_date AS TEXT)),
         UPPER(f.name),
         o.order_date DESC;
"""
 
def slow_query():
    conn = _get_conn()
    cur = conn.cursor()
    start = time.time()
    try:
        cur.execute(SLOW_SQL)
        cur.fetchall()
        elapsed = time.time() - start
        return {"sql": SLOW_SQL.strip(), "elapsed": round(elapsed, 4)}
    except Exception as e:
        elapsed = time.time() - start
        return {"sql": SLOW_SQL.strip(), "elapsed": round(elapsed, 4), "error": str(e)}
    finally:
        cur.close()
        conn.close()