import psycopg2

DATABASE_URL = (
    "postgresql://neondb_owner:npg_M5sVheSzQLv4@"
    "ep-shrill-tree-a819xf7v-pooler.eastus2.azure.neon.tech/"
    "neondb?sslmode=require"
)

def _get_conn():
    return psycopg2.connect(DATABASE_URL)


def insert_flower(name, color, price):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        sql = f"""
            INSERT INTO team10_flower (name, color, price)
            VALUES ('{name}', '{color}', {price});
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
            sql = """
                SELECT id, name, last_watered, water_level, min_water_required
                FROM team10_flower
                ORDER BY id;
            """
            cur.execute(sql)
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
                SELECT id, name, last_watered, water_level, min_water_required
                FROM team10_flower
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


def update_flower(flower_id, name, color, price):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        sql = f"""
            UPDATE team10_flower
            SET name = '{name}',
                color = '{color}',
                price = {price}
            WHERE flower_id = {flower_id};
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


def delete_flower(flower_id):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        sql = f"""
            DELETE FROM team10_flower
            WHERE flower_id = {flower_id};
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