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


def select_flower(id=None):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        if id is None:
            sql = """
                UPDATE team11_flowers
                SET water_level = water_level - (5 * (CURRENT_DATE - last_watered));
                SELECT id, name, color, price, water_level, min_water_required
                FROM team11_flowers
                ORDER BY id;
            """
            cur.execute(sql)
            rows = cur.fetchall()
            return [
                {
                    "id": r[0],
                    "name": r[1],
                    "color": r[2],
                    "price": r[3],
                    "water_level": r[4],
                    "min_water_required": r[5]
                }
                for r in rows
            ]
        else:
            sql = f"""
                SELECT id, name, color, price, water_level, min_water_required
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
                "color": row[2],
                "price": row[3],
                "water_level": row[4],
                "min_water_required": row[5]
            }
    finally:
        cur.close()
        conn.close()


def update_flower(id, name, color, price):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        sql = f"""
            UPDATE Flower
            SET name = '{name}',
                color = '{color}',
                price = {price}
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
            DELETE FROM Flower
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
            SET water_level = 20
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