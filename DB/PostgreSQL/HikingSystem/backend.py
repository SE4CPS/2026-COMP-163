import os
import sqlite3

SQLITE_PATH = os.environ.get("SQLITE_PATH", "local.db")


def _conn():
    return sqlite3.connect(SQLITE_PATH)


# -----------------------------
# Trail CRUD
# -----------------------------

def insert_trail(name, difficulty, capacity):
    conn = _conn()
    cur = conn.cursor()
    try:
        difficulty = (difficulty or "Easy").strip() or "Easy"
        capacity = int(capacity)
        sql = f"""
            INSERT INTO Trail (name, difficulty, capacity)
            VALUES ('{name}', '{difficulty}', {capacity});
        """
        cur.execute(sql)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Insert trail error:", e)
        return False
    finally:
        cur.close()
        conn.close()


def select_trails(trail_id=None):
    conn = _conn()
    cur = conn.cursor()
    try:
        if trail_id is None:
            cur.execute("""
                SELECT trail_id, name, difficulty, capacity
                FROM Trail
                ORDER BY trail_id;
            """)
            rows = cur.fetchall()
            return [
                {"trail_id": r[0], "name": r[1], "difficulty": r[2], "capacity": r[3]}
                for r in rows
            ]
        else:
            cur.execute(f"""
                SELECT trail_id, name, difficulty, capacity
                FROM Trail
                WHERE trail_id = {trail_id};
            """)
            r = cur.fetchone()
            if not r:
                return None
            return {"trail_id": r[0], "name": r[1], "difficulty": r[2], "capacity": r[3]}
    finally:
        cur.close()
        conn.close()


def delete_trail(trail_id):
    conn = _conn()
    cur = conn.cursor()
    try:
        cur.execute(f"DELETE FROM Trail WHERE trail_id = {trail_id};")
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Delete trail error:", e)
        return False
    finally:
        cur.close()
        conn.close()


# -----------------------------
# Reservation CRUD
# -----------------------------

def insert_reservation(hiker_name, hike_date, trail_id):
    conn = _conn()
    cur = conn.cursor()
    try:
        trail_id = int(trail_id)
        sql = f"""
            INSERT INTO Reservation (hiker_name, hike_date, trail_id)
            VALUES ('{hiker_name}', '{hike_date}', {trail_id});
        """
        cur.execute(sql)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Insert reservation error:", e)
        return False
    finally:
        cur.close()
        conn.close()


def delete_reservation(reservation_id):
    conn = _conn()
    cur = conn.cursor()
    try:
        cur.execute(f"DELETE FROM Reservation WHERE reservation_id = {reservation_id};")
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Delete reservation error:", e)
        return False
    finally:
        cur.close()
        conn.close()


# -----------------------------
# JOIN (practice)
# -----------------------------

def select_reservations_join():
    """
    JOIN Reservation -> Trail so students can practice:
      SELECT ... FROM Reservation r JOIN Trail t ON r.trail_id = t.trail_id;
    """
    conn = _conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT
                r.reservation_id,
                r.hiker_name,
                r.hike_date,
                t.trail_id,
                t.name AS trail_name,
                t.difficulty,
                t.capacity
            FROM Reservation r INNER JOIN Trail t
            ON r.trail_id = t.trail_id
            ORDER BY r.hike_date, r.reservation_id;
        """)
        rows = cur.fetchall()
        return [
            {
                "reservation_id": r[0],
                "hiker_name": r[1],
                "hike_date": r[2],
                "trail_id": r[3],
                "trail_name": r[4],
                "difficulty": r[5],
                "capacity": r[6],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()
