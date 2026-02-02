"""
Minimal Flask + SQLite app:
- Creates a Furniture table (if not exists)
- Generates sample data (button on the page)
- Shows current rows on a simple web page

Run:
  pip install flask
  python app.py
Open:
  http://127.0.0.1:5000
"""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from typing import List, Tuple

from flask import Flask, redirect, render_template_string, request, url_for

APP = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "furniture.db")


# -----------------------------
# Database helpers (simple)
# -----------------------------
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS Furniture (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                name     TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL DEFAULT 'General',
                price    REAL NOT NULL CHECK (price >= 0)
            );
            """
        )


def seed_data() -> None:
    """
    Insert a small set of rows. Uses INSERT OR IGNORE so it is safe to click multiple times.
    """
    items = [
        ("Chair", "Seating", 39.99),
        ("Table", "Surface", 129.00),
        ("Desk", "Surface", 199.50),
        ("Sofa", "Seating", 599.00),
        ("Lamp", "Lighting", 24.95),
    ]
    with get_conn() as conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO Furniture (name, category, price)
            VALUES (?, ?, ?);
            """,
            items,
        )


def fetch_all() -> List[sqlite3.Row]:
    with get_conn() as conn:
        return list(conn.execute("SELECT id, name, category, price FROM Furniture ORDER BY id;"))


def clear_all() -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM Furniture;")


# -----------------------------
# Web UI (single page)
# -----------------------------
PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Furniture DB Demo</title>
  <style>
    body { font-family: system-ui, Arial, sans-serif; margin: 2rem; }
    .bar { display:flex; gap: .75rem; align-items:center; margin: 1rem 0 1.25rem; flex-wrap: wrap; }
    button { padding: .5rem .8rem; cursor: pointer; }
    table { border-collapse: collapse; width: 100%; max-width: 900px; }
    th, td { border: 1px solid #ccc; padding: .5rem .6rem; text-align: left; }
    th { background: #f6f6f6; }
    .muted { color: #666; font-size: .95rem; }
    .pill { display:inline-block; padding:.1rem .5rem; border:1px solid #ccc; border-radius: 999px; font-size:.9rem; }
    form { margin: 0; }
    input { padding: .45rem .55rem; }
  </style>
</head>
<body>
  <h2>Furniture Database (SQLite)</h2>
  <div class="muted">
    One table: <span class="pill">Furniture(id, name, category, price)</span>
  </div>

  <div class="bar">
    <form method="post" action="{{ url_for('seed') }}">
      <button type="submit">Generate Sample Data</button>
    </form>

    <form method="post" action="{{ url_for('clear') }}">
      <button type="submit">Clear Table</button>
    </form>

    <form method="post" action="{{ url_for('add') }}">
      <input name="name" placeholder="Name (unique)" required />
      <input name="category" placeholder="Category" />
      <input name="price" placeholder="Price" type="number" step="0.01" min="0" required />
      <button type="submit">Add One Item</button>
    </form>
  </div>

  {% if error %}
    <p style="color:#b00020;"><strong>Error:</strong> {{ error }}</p>
  {% endif %}

  <p><strong>{{ rows|length }}</strong> row(s)</p>

  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>Name</th>
        <th>Category</th>
        <th>Price</th>
      </tr>
    </thead>
    <tbody>
      {% for r in rows %}
        <tr>
          <td>{{ r["id"] }}</td>
          <td>{{ r["name"] }}</td>
          <td>{{ r["category"] }}</td>
          <td>${{ "%.2f"|format(r["price"]) }}</td>
        </tr>
      {% endfor %}
      {% if rows|length == 0 %}
        <tr>
          <td colspan="4" class="muted">No rows yet. Click “Generate Sample Data”.</td>
        </tr>
      {% endif %}
    </tbody>
  </table>
</body>
</html>
"""


# -----------------------------
# Flask routes
# -----------------------------
@APP.get("/")
def index():
    init_db()
    rows = fetch_all()
    # show an error message if passed as query param
    error = request.args.get("error", "")
    return render_template_string(PAGE, rows=rows, error=error)


@APP.post("/seed")
def seed():
    init_db()
    seed_data()
    return redirect(url_for("index"))


@APP.post("/clear")
def clear():
    init_db()
    clear_all()
    return redirect(url_for("index"))


@APP.post("/add")
def add():
    init_db()
    name = (request.form.get("name") or "").strip()
    category = (request.form.get("category") or "").strip() or "General"
    price_raw = (request.form.get("price") or "").strip()

    try:
        price = float(price_raw)
        if price < 0:
            raise ValueError("Price must be >= 0")
    except Exception:
        return redirect(url_for("index", error="Invalid price."))

    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO Furniture (name, category, price) VALUES (?, ?, ?);",
                (name, category, price),
            )
    except sqlite3.IntegrityError as e:
        # UNIQUE / NOT NULL / CHECK errors land here
        return redirect(url_for("index", error=str(e)))

    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    APP.run(debug=True)
