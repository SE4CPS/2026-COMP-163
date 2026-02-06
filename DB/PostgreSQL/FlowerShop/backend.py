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
            INSERT INTO Flower (name, color, price)
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


def select_flower(flower_id=None):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        if flower_id is None:
            sql = """
                SELECT flower_id, name, color, price
                FROM Flower
                ORDER BY flower_id;
            """
            cur.execute(sql)
            rows = cur.fetchall()
            return [
                {
                    "flower_id": r[0],
                    "name": r[1],
                    "color": r[2],
                    "price": r[3],
                }
                for r in rows
            ]
        else:
            sql = f"""
                SELECT flower_id, name, color, price
                FROM Flower
                WHERE flower_id = {flower_id};
            """
            cur.execute(sql)
            row = cur.fetchone()
            if not row:
                return None
            return {
                "flower_id": row[0],
                "name": row[1],
                "color": row[2],
                "price": row[3],
            }
    finally:
        cur.close()
        conn.close()


def update_flower(flower_id, name, color, price):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        sql = f"""
            UPDATE Flower
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
            DELETE FROM Flower
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