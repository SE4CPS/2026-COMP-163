import psycopg2

DATABASE_URL = (
    "postgresql://neondb_owner:npg_M5sVheSzQLv4@"
    "ep-shrill-tree-a819xf7v-pooler.eastus2.azure.neon.tech/"
    "neondb?sslmode=require"
)

TEAM_TABLE = "team2_flowers"

def _get_conn():
    return psycopg2.connect(DATABASE_URL)


def insert_flower(name, color, price, last_watered=None, water_level=10, min_water_required=5):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        import datetime
        if last_watered is None:
            last_watered = datetime.date.today().isoformat()
        cur.execute("""
            INSERT INTO team2_flowers (name, color, price, last_watered, water_level, min_water_required)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (name, color, price, last_watered, water_level, min_water_required))
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
            cur.execute("""
                SELECT id, name, color, price
                FROM team2_flowers
                ORDER BY id;
            """)
            rows = cur.fetchall()
            return [
                {"flower_id": r[0], "name": r[1], "color": r[2], "price": r[3]}
                for r in rows
            ]
        else:
            cur.execute("""
                SELECT id, name, color, price
                FROM team2_flowers
                WHERE id = %s;
            """, (flower_id,))
            row = cur.fetchone()
            if not row:
                return None
            return {"flower_id": row[0], "name": row[1], "color": row[2], "price": row[3]}
    finally:
        cur.close()
        conn.close()

def update_flower(flower_id, name, color, price):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE team2_flowers
            SET name = %s, color = %s, price = %s
            WHERE id = %s;
        """, (name, color, price, flower_id))
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
            DELETE FROM team2_flowers 
            WHERE id = {flower_id};
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


# ----------------------------
# Step 4 Flask API (team2_flowers)
# ----------------------------

def _format_date(d):
    # d is usually a python date from psycopg2
    return d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else d


def get_flowers_api(needs_only: bool = False):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        if needs_only:
            cur.execute(
                f"""
                SELECT id, name, last_watered, water_level, min_water_required
                FROM {TEAM_TABLE}
                WHERE water_level < min_water_required
                ORDER BY id;
                """
            )
        else:
            cur.execute(
                f"""
                SELECT id, name, last_watered, water_level, min_water_required
                FROM {TEAM_TABLE}
                ORDER BY id;
                """
            )

        rows = cur.fetchall()
        return [
            {
                "id": r[0],
                "name": r[1],
                "last_watered": _format_date(r[2]),
                "water_level": r[3],
                "needs_watering": r[3] < r[4],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


def add_flower_api(name, color, price, last_watered, water_level, min_water_required):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            INSERT INTO {TEAM_TABLE} (name, color, price, last_watered, water_level, min_water_required)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (name, color, price, last_watered, water_level, min_water_required),
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    except Exception as e:
        conn.rollback()
        print("Add error:", e)
        return None
    finally:
        cur.close()
        conn.close()


def update_flower_api(id, last_watered, water_level, min_water_required=None):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        if min_water_required is None:
            cur.execute(
                f"""
                UPDATE {TEAM_TABLE}
                SET last_watered = %s,
                    water_level = %s
                WHERE id = %s;
                """,
                (last_watered, water_level, id),
            )
        else:
            cur.execute(
                f"""
                UPDATE {TEAM_TABLE}
                SET last_watered = %s,
                    water_level = %s,
                    min_water_required = %s
                WHERE id = %s;
                """,
                (last_watered, water_level, min_water_required, id),
            )

        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        print("Update error:", e)
        return False
    finally:
        cur.close()
        conn.close()


def delete_flower_api(id):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute(f"DELETE FROM {TEAM_TABLE} WHERE id = %s;", (id,),) #added comma to make it a tuple
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        print("Delete error:", e)
        return False
    finally:
        cur.close()
        conn.close()


def daily_watering_check():
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            UPDATE {TEAM_TABLE}
            SET water_level = GREATEST(0, water_level - (5 * (CURRENT_DATE - last_watered)));

            
            """
           # WHERE water_level < min_water_required;
        )
        conn.commit()
        return cur.rowcount
    except Exception as e:
        conn.rollback()
        print("Daily check error:", e)
        return 0
    finally:
        cur.close()
        conn.close()