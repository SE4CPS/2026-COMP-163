import os
import sqlite3
import psycopg2

# -----------------------------------------
# Config
# -----------------------------------------

DATABASE_URL = (
    "postgresql://neondb_owner:npg_M5sVheSzQLv4@"
    "ep-shrill-tree-a819xf7v-pooler.eastus2.azure.neon.tech/"
    "neondb?sslmode=require"
)

SQLITE_PATH = os.environ.get("SQLITE_PATH", "local.db")

# Choose where writes go and where reads come from:
#   BACKEND_MODE=sqlite   -> use only local sqlite
#   BACKEND_MODE=pg       -> use only postgres
#   BACKEND_MODE=both     -> write to both; read from sqlite by default
MODE = os.environ.get("BACKEND_MODE", "sqlite").lower()


# -----------------------------------------
# Connections
# -----------------------------------------

def _pg_conn():
    return psycopg2.connect(DATABASE_URL)

def _sqlite_conn():
    # row_factory lets us read by column name if we want later
    conn = sqlite3.connect(SQLITE_PATH)
    return conn


# -----------------------------------------
# Admin helpers (schema/seed)  safe to call at startup
# -----------------------------------------

def init_db():
    """Create table in whichever DB(s) MODE implies."""
    if MODE in ("pg", "both"):
        conn = _pg_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Flower (
                flower_id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                color TEXT NOT NULL DEFAULT 'Mixed',
                price NUMERIC(10,2) NOT NULL CHECK (price >= 0)
            );
        """)
        conn.commit()
        cur.close()
        conn.close()

    if MODE in ("sqlite", "both"):
        conn = _sqlite_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Flower (
                flower_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT NOT NULL DEFAULT 'Mixed',
                price REAL NOT NULL CHECK (price >= 0)
            );
        """)
        conn.commit()
        cur.close()
        conn.close()

def seed_data():
    """Insert default data (idempotent) into whichever DB(s) MODE implies."""
    if MODE in ("pg", "both"):
        conn = _pg_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Flower (name, color, price)
            VALUES
                ('Rose', 'Red', 4.99),
                ('Tulip', 'Yellow', 3.50),
                ('Lily', 'White', 5.25)
            ON CONFLICT (name) DO NOTHING;
        """)
        conn.commit()
        cur.close()
        conn.close()

    if MODE in ("sqlite", "both"):
        conn = _sqlite_conn()
        cur = conn.cursor()
        # SQLite flavor: INSERT OR IGNORE for idempotent seed
        cur.execute("""
            INSERT OR IGNORE INTO Flower (name, color, price)
            VALUES
                ('Rose', 'Red', 4.99),
                ('Tulip', 'Yellow', 3.50),
                ('Lily', 'White', 5.25);
        """)
        conn.commit()
        cur.close()
        conn.close()


# -----------------------------------------
# CRUD (plain SQL strings, no %s)
# -----------------------------------------

def insert_flower(name, color, price):
    ok = True

    if MODE in ("pg", "both"):
        conn = _pg_conn()
        cur = conn.cursor()
        try:
            sql = f"""
                INSERT INTO Flower (name, color, price)
                VALUES ('{name}', '{color}', {price});
            """
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            ok = False
            conn.rollback()
            print("PG insert error:", e)
        finally:
            cur.close()
            conn.close()

    if MODE in ("sqlite", "both"):
        conn = _sqlite_conn()
        cur = conn.cursor()
        try:
            sql = f"""
                INSERT INTO Flower (name, color, price)
                VALUES ('{name}', '{color}', {price});
            """
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            ok = False
            conn.rollback()
            print("SQLite insert error:", e)
        finally:
            cur.close()
            conn.close()

    return ok


def select_flower(flower_id=None, source=None):
    """
    source controls where reads come from:
      source=None      -> uses MODE default (sqlite for both)
      source="sqlite"  -> force local
      source="pg"      -> force postgres
    """
    src = (source or ("sqlite" if MODE == "both" else MODE)).lower()

    if src == "pg":
        conn = _pg_conn()
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
                return [{"flower_id": r[0], "name": r[1], "color": r[2], "price": r[3]} for r in rows]
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
                return {"flower_id": row[0], "name": row[1], "color": row[2], "price": row[3]}
        finally:
            cur.close()
            conn.close()

    # default: sqlite
    conn = _sqlite_conn()
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
            return [{"flower_id": r[0], "name": r[1], "color": r[2], "price": r[3]} for r in rows]
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
            return {"flower_id": row[0], "name": row[1], "color": row[2], "price": row[3]}
    finally:
        cur.close()
        conn.close()


def update_flower(flower_id, name, color, price):
    ok = True

    if MODE in ("pg", "both"):
        conn = _pg_conn()
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
        except Exception as e:
            ok = False
            conn.rollback()
            print("PG update error:", e)
        finally:
            cur.close()
            conn.close()

    if MODE in ("sqlite", "both"):
        conn = _sqlite_conn()
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
        except Exception as e:
            ok = False
            conn.rollback()
            print("SQLite update error:", e)
        finally:
            cur.close()
            conn.close()

    return ok


def delete_flower(flower_id):
    ok = True

    if MODE in ("pg", "both"):
        conn = _pg_conn()
        cur = conn.cursor()
        try:
            sql = f"DELETE FROM Flower WHERE flower_id = {flower_id};"
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            ok = False
            conn.rollback()
            print("PG delete error:", e)
        finally:
            cur.close()
            conn.close()

    if MODE in ("sqlite", "both"):
        conn = _sqlite_conn()
        cur = conn.cursor()
        try:
            sql = f"DELETE FROM Flower WHERE flower_id = {flower_id};"
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            ok = False
            conn.rollback()
            print("SQLite delete error:", e)
        finally:
            cur.close()
            conn.close()

    return ok