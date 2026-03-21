import psycopg2

DATABASE_URL = (
    "postgresql://neondb_owner:npg_M5sVheSzQLv4@"
    "ep-shrill-tree-a819xf7v-pooler.eastus2.azure.neon.tech/"
    "neondb?sslmode=require"
)

def _get_conn():
    return psycopg2.connect(DATABASE_URL)

def insert_flower(name, last_watered, water_level, min_water_required):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO team10_flowers (name, last_watered, water_level, min_water_required)
            VALUES (%s, %s, %s, %s);
        """, (name, last_watered, water_level, min_water_required))
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
            cur.execute("""
                SELECT id, name, last_watered, water_level, min_water_required, current_water_level
                FROM v_team10_flowers ORDER BY id;
            """)
            rows = cur.fetchall()
            return [{
                "id": r[0],
                "name": r[1],
                "last_watered": r[2].strftime("%Y-%m-%d"), 
                "water_level": r[3],
                "min_water_required": r[4],
                "current_water_level": r[5],
                "needs_watering": r[5] < r[4]
            } for r in rows]
        else:
            cur.execute("SELECT id, name, last_watered, water_level, min_water_required, current_water_level FROM v_team10_flowers WHERE id = %s;", (id,))
            row = cur.fetchone()
            if not row:
                return None
            return {"id": row[0], "name": row[1], "last_watered": row[2].strftime("%Y-%m-%d"), "water_level": row[3], "min_water_required": row[4], "current_water_level": row[5], "needs_watering": row[5] < row[4]}
    finally:
        cur.close()
        conn.close()

def update_flower(id, last_watered, water_level):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE team10_flowers SET last_watered = %s, water_level = %s WHERE id = %s;", (last_watered, water_level, id))
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
        cur.execute("DELETE FROM team10_flowers WHERE id = %s;", (id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Delete error:", e)
        return False
    finally:
        cur.close()
        conn.close()

def water_flower(id, amount):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE team10_flowers AS t
            SET water_level = v.current_water_level + %s,
                    last_watered = CURRENT_DATE
            FROM v_team10_flowers AS v
            WHERE t.id = v.id
            AND t.id = %s;
        """, (amount, id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Water error:", e)
        return False
    finally:
        cur.close()
        conn.close()
