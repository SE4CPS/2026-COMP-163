import os
import sqlite3

# Simple local SQLite DB (good for practice)
SQLITE_PATH = os.environ.get("SQLITE_PATH", "local.db")


def _conn():
    return sqlite3.connect(SQLITE_PATH)


def init_db():
    conn = _conn()
    cur = conn.cursor()

    # Two tables for JOIN practice: Trail and Reservation
    cur.execute("""
        DROP TABLE IF EXISTS Trail;
    """)

    cur.execute("""
        CREATE TABLE Trail (
            trail_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            difficulty TEXT NOT NULL DEFAULT 'Easy',
            capacity INTEGER NOT NULL DEFAULT 10 CHECK (capacity >= 0),
            weather TEXT DEFAULT 'Sunny'
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Reservation (
            reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            hiker_name TEXT NOT NULL,
            hike_date TEXT NOT NULL,              -- keep as TEXT for simplicity (YYYY-MM-DD)
            trail_id INTEGER NOT NULL,
            FOREIGN KEY (trail_id) REFERENCES Trail(trail_id)
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


def seed_data():
    conn = _conn()
    cur = conn.cursor()

    # Trails (idempotent)
    cur.execute("""
        INSERT OR IGNORE INTO Trail (name, difficulty, capacity)
        VALUES
            ('Pine Ridge Loop', 'Easy', 12),
            ('Eagle Peak', 'Hard', 6),
            ('River Walk', 'Easy', 20);
    """)

    # Reservations (only insert if table empty to keep it simple)
    cur.execute("SELECT COUNT(*) FROM Reservation;")
    count = cur.fetchone()[0]
    if count == 0:
        cur.execute("""
            INSERT INTO Reservation (hiker_name, hike_date, trail_id)
            VALUES
                ('Ava', '2026-02-15', 1),
                ('Noah', '2026-02-16', 2),
                ('Mia', '2026-02-16', 1);
        """)

    conn.commit()
    cur.close()
    conn.close()
