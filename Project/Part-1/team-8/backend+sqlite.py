import os
import sqlite3
import psycopg2

# -----------------------------------------
# Config
# -----------------------------------------
# Keep this file as an "optional" version:
# - BACKEND_MODE=sqlite (default): easiest locally
# - BACKEND_MODE=pg: use Postgres
# - BACKEND_MODE=both: write to both; read from sqlite by default

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
SQLITE_PATH = os.environ.get("SQLITE_PATH", "local.db")
MODE = os.environ.get("BACKEND_MODE", "sqlite").lower()


# -----------------------------------------
# Connections
# -----------------------------------------

def _pg_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is empty. Set it to use BACKEND_MODE=pg or both.")
    return psycopg2.connect(DATABASE_URL)

def _sqlite_conn():
    return sqlite3.connect(SQLITE_PATH)


# -----------------------------------------
# Admin helpers (schema/seed)
# -----------------------------------------

def init_db():
    if MODE in ("pg", "both"):
        conn = _pg_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Trail (
                trail_id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                difficulty TEXT NOT NULL DEFAULT 'Easy',
                capacity INTEGER NOT NULL DEFAULT 10 CHECK (capacity >= 0)
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Reservation (
                reservation_id SERIAL PRIMARY KEY,
                hiker_name TEXT NOT NULL,
                hike_date TEXT NOT NULL,
                trail_id INTEGER NOT NULL REFERENCES Trail(trail_id)
            );
        """)
        conn.commit()
        cur.close()
        conn.close()

    if MODE in ("sqlite", "both"):
        conn = _sqlite_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Trail (
                trail_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                difficulty TEXT NOT NULL DEFAULT 'Easy',
                capacity INTEGER NOT NULL DEFAULT 10 CHECK (capacity >= 0)
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Reservation (
                reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                hiker_name TEXT NOT NULL,
                hike_date TEXT NOT NULL,
                trail_id INTEGER NOT NULL,
                FOREIGN KEY (trail_id) REFERENCES Trail(trail_id)
            );
        """)
        conn.commit()
        cur.close()
        conn.close()


def seed_data():
    # Trails (idempotent)
    if MODE in ("pg", "both"):
        conn = _pg_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Trail (name, difficulty, capacity)
            VALUES
                ('Pine Ridge Loop', 'Easy', 12),
                ('Eagle Peak', 'Hard', 6),
                ('River Walk', 'Easy', 20)
            ON CONFLICT (name) DO NOTHING;
        """)
        conn.commit()
        cur.close()
        conn.close()

    if MODE in ("sqlite", "both"):
        conn = _sqlite_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO Trail (name, difficulty, capacity)
            VALUES
                ('Pine Ridge Loop', 'Easy', 12),
                ('Eagle Peak', 'Hard', 6),
                ('River Walk', 'Easy', 20);
        """)
        conn.commit()
        cur.close()
        conn.close()


# -----------------------------------------
# CRUD + JOIN (plain f-strings for practice)
# -----------------------------------------

def insert_trail(name, difficulty, capacity):
    ok = True

    if MODE in ("pg", "both"):
        conn = _pg_conn()
        cur = conn.cursor()
        try:
            sql = f"INSERT INTO Trail (name, difficulty, capacity) VALUES ('{name}', '{difficulty}', {int(capacity)});"
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            ok = False
            conn.rollback()
            print("PG insert trail error:", e)
        finally:
            cur.close()
            conn.close()

    if MODE in ("sqlite", "both"):
        conn = _sqlite_conn()
        cur = conn.cursor()
        try:
            sql = f"INSERT INTO Trail (name, difficulty, capacity) VALUES ('{name}', '{difficulty}', {int(capacity)});"
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            ok = False
            conn.rollback()
            print("SQLite insert trail error:", e)
        finally:
            cur.close()
            conn.close()

    return ok


def select_trails(source=None):
    src = (source or ("sqlite" if MODE == "both" else MODE)).lower()

    if src == "pg":
        conn = _pg_conn()
        cur = conn.cursor()
        try:
            cur.execute("SELECT trail_id, name, difficulty, capacity FROM Trail ORDER BY trail_id;")
            rows = cur.fetchall()
            return [{"trail_id": r[0], "name": r[1], "difficulty": r[2], "capacity": r[3]} for r in rows]
        finally:
            cur.close()
            conn.close()

    conn = _sqlite_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT trail_id, name, difficulty, capacity FROM Trail ORDER BY trail_id;")
        rows = cur.fetchall()
        return [{"trail_id": r[0], "name": r[1], "difficulty": r[2], "capacity": r[3]} for r in rows]
    finally:
        cur.close()
        conn.close()


def insert_reservation(hiker_name, hike_date, trail_id):
    ok = True

    if MODE in ("pg", "both"):
        conn = _pg_conn()
        cur = conn.cursor()
        try:
            sql = f"INSERT INTO Reservation (hiker_name, hike_date, trail_id) VALUES ('{hiker_name}', '{hike_date}', {int(trail_id)});"
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            ok = False
            conn.rollback()
            print("PG insert reservation error:", e)
        finally:
            cur.close()
            conn.close()

    if MODE in ("sqlite", "both"):
        conn = _sqlite_conn()
        cur = conn.cursor()
        try:
            sql = f"INSERT INTO Reservation (hiker_name, hike_date, trail_id) VALUES ('{hiker_name}', '{hike_date}', {int(trail_id)});"
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            ok = False
            conn.rollback()
            print("SQLite insert reservation error:", e)
        finally:
            cur.close()
            conn.close()

    return ok


def delete_reservation(reservation_id):
    ok = True

    if MODE in ("pg", "both"):
        conn = _pg_conn()
        cur = conn.cursor()
        try:
            cur.execute(f"DELETE FROM Reservation WHERE reservation_id = {int(reservation_id)};")
            conn.commit()
        except Exception as e:
            ok = False
            conn.rollback()
            print("PG delete reservation error:", e)
        finally:
            cur.close()
            conn.close()

    if MODE in ("sqlite", "both"):
        conn = _sqlite_conn()
        cur = conn.cursor()
        try:
            cur.execute(f"DELETE FROM Reservation WHERE reservation_id = {int(reservation_id)};")
            conn.commit()
        except Exception as e:
            ok = False
            conn.rollback()
            print("SQLite delete reservation error:", e)
        finally:
            cur.close()
            conn.close()

    return ok


def select_reservations_join(source=None):
    src = (source or ("sqlite" if MODE == "both" else MODE)).lower()

    sql = """
        SELECT
            r.reservation_id,
            r.hiker_name,
            r.hike_date,
            t.trail_id,
            t.name AS trail_name,
            t.difficulty,
            t.capacity
        FROM Reservation r
        JOIN Trail t ON r.trail_id = t.trail_id
        ORDER BY r.hike_date, r.reservation_id;
    """

    if src == "pg":
        conn = _pg_conn()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            rows = cur.fetchall()
            return [{"reservation_id": r[0], "hiker_name": r[1], "hike_date": r[2], "trail_id": r[3],
                     "trail_name": r[4], "difficulty": r[5], "capacity": r[6]} for r in rows]
        finally:
            cur.close()
            conn.close()

    conn = _sqlite_conn()
    cur = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        return [{"reservation_id": r[0], "hiker_name": r[1], "hike_date": r[2], "trail_id": r[3],
                 "trail_name": r[4], "difficulty": r[5], "capacity": r[6]} for r in rows]
    finally:
        cur.close()
        conn.close()
