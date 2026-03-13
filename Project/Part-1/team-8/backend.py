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
        sql = f"""
            INSERT INTO team8_flowers (name, last_watered, water_level, min_water_required)
            VALUES ('{name}', '{last_watered}', {water_level}, {min_water_required});
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
    daily_water_update()
    conn = _get_conn()
    cur = conn.cursor()
    try:
        if flower_id is None:
            sql = """
                SELECT flower_id, name, last_watered, water_level, min_water_required
                FROM team8_flowers
                ORDER BY flower_id;
            """
            cur.execute(sql)
            rows = cur.fetchall()
            return [
                {
                    "flower_id": r[0],
                    "name": r[1],
                    "last_watered": r[2],
                    "water_level": r[3],
                    "min_water_required": r[4]
                }
                for r in rows
            ]
        else:
            sql = f"""
                SELECT flower_id, name, last_watered, water_level, min_water_required
                FROM team8_flowers
                WHERE flower_id = {flower_id};
            """
            cur.execute(sql)
            row = cur.fetchone()
            if not row:
                return None
            return [
                {
                    "flower_id": r[0],
                    "name": r[1],
                    "last_watered": r[2],
                    "water_level": r[3],
                    "min_water_required": r[4]
                }
                for r in rows
            ]
    finally:
        cur.close()
        conn.close()


def update_flower(flower_id, name, last_watered, water_level, min_water_required):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        sql = f"""
            UPDATE team8_flowers
            SET name = '{name}',
                last_watered = '{last_watered}',
                water_level = {water_level},
                min_water_required = {min_water_required}
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
            DELETE FROM team8_flowers
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

def water_flower(flower_id):
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE team8_flowers
        SET water_level = water_level + 10,
            last_watered = CURRENT_DATE
        WHERE flower_id = %s;
    """, (flower_id,))

    conn.commit()
    cur.close()
    conn.close()

def daily_water_update():
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE team8_flowers
        SET water_level = GREATEST(water_level - (5 * (CURRENT_DATE - last_watered)),
        0)
        WHERE CURRENT_DATE > last_watered;
    """)

    conn.commit()
    cur.close()
    conn.close()