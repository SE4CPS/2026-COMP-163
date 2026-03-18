import psycopg2
from datetime import date

DATABASE_URL = (
    "postgresql://neondb_owner:npg_M5sVheSzQLv4@"
    "ep-shrill-tree-a819xf7v-pooler.eastus2.azure.neon.tech/"
    "neondb?sslmode=require"
)

def _get_conn():
    return psycopg2.connect(DATABASE_URL)

def insert_flower(name, water_level=20, min_water_required=5):
    """Insert a new flower with default water level and minimum required"""
    conn = _get_conn()
    cur = conn.cursor()
    try:
        sql = """
            INSERT INTO team3_flowers (name, last_watered, water_level, min_water_required)
            VALUES (%s, %s, %s, %s);
        """
        cur.execute(sql, (name, date.today(), water_level, min_water_required))
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
    """Get one or all flowers"""
    conn = _get_conn()
    cur = conn.cursor()
    try:
        if id is None:
            sql = """
                SELECT id, name, last_watered, water_level, min_water_required
                FROM team3_flowers
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
            sql = """
                SELECT id, name, last_watered, water_level, min_water_required
                FROM team3_flowers
                WHERE id = %s;
            """
            cur.execute(sql, (id,))
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

def update_flower(id, name, water_level=None, min_water_required=None):
    """Update flower details"""
    conn = _get_conn()
    cur = conn.cursor()
    try:
        sql = """
            UPDATE team3_flowers
            SET name = %s,
                water_level = %s,
                min_water_required = %s
            WHERE id = %s;
        """
        cur.execute(sql, (name, water_level, min_water_required, id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Update error:", e)
        return False
    finally:
        cur.close()
        conn.close()

def water_flower(id, amount=10):
    """Add water to a flower and update last_watered timestamp"""
    conn = _get_conn()
    cur = conn.cursor()
    try:
        sql = """
            UPDATE team3_flowers
            SET water_level = COALESCE(water_level, 0) + %s,
                last_watered = %s
            WHERE id = %s;
        """
        cur.execute(sql, (amount, date.today(), id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Water error:", e)
        return False
    finally:
        cur.close()
        conn.close()

def get_flowers_needing_water():
    """Get all flowers where water_level is below min_water_required"""
    conn = _get_conn()
    cur = conn.cursor()
    try:
        sql = """
            SELECT id, name, last_watered, water_level, min_water_required
            FROM team3_flowers
            WHERE water_level < min_water_required
            ORDER BY water_level ASC;
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
    finally:
        cur.close()
        conn.close()

def delete_flower(id):
    """Delete a flower by ID"""
    conn = _get_conn()
    cur = conn.cursor()
    try:
        sql = """
            DELETE FROM team3_flowers
            WHERE id = %s;
        """
        cur.execute(sql, (id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Delete error:", e)
        return False
    finally:
        cur.close()
        conn.close()