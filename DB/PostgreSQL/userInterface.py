"""
Minimal Flask app using Neon Postgres *REST API* (PostgREST).

You gave this base URL:
  https://ep-shrill-tree-a819xf7v.apirest.eastus2.azure.neon.tech/neondb/rest/v1

This app:
- Reads rows from /furniture and shows them on a web page
- Can insert sample rows (button)
- Can insert one row from a small form
- Can clear the table (button)

IMPORTANT (traditional reality check):
- PostgREST is for data access (SELECT/INSERT/UPDATE/DELETE).
- Creating the table (DDL) is typically done once in Neon SQL Editor / console.
  The app below will *detect* if the table is missing and show a message.

Prereqs:
  pip install flask requests

Environment variables (must be set):
  export NEON_REST_BASE="https://ep-shrill-tree-a819xf7v.apirest.eastus2.azure.neon.tech/neondb/rest/v1"
  export NEON_API_KEY="YOUR_NEON_API_KEY"

Run:
  python app_postgres_rest.py

Open:
  http://127.0.0.1:5000/
"""

from __future__ import annotations

import os
import requests
from flask import Flask, redirect, render_template_string, request, url_for

app = Flask(__name__)

BASE = os.environ.get(
    "NEON_REST_BASE",
    "https://ep-shrill-tree-a819xf7v.apirest.eastus2.azure.neon.tech/neondb/rest/v1",
).rstrip("/")

API_KEY = os.environ.get("NEON_API_KEY", "").strip()

PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Furniture (Neon Postgres via REST)</title>
  <style>
    body { font-family: system-ui, Arial, sans-serif; margin: 2rem; }
    .bar { display:flex; gap: .75rem; align-items:center; margin: 1rem 0 1.25rem; flex-wrap: wrap; }
    button { padding: .5rem .8rem; cursor: pointer; }
    input { padding: .45rem .55rem; }
    table { border-collapse: collapse; width: 100%; max-width: 900px; }
    th, td { border: 1px solid #ccc; padding: .5rem .6rem; text-align: left; }
    th { background: #f6f6f6; }
    .muted { color:#666; }
    code { background:#f6f6f6; padding:.1rem .35rem; border-radius:6px; }
  </style>
</head>
<body>
  <h2>Furniture (Neon Postgres via REST)</h2>

  <p class="muted">
    Base: <code>{{ base }}</code>
  </p>

  {% if fatal %}
    <p style="color:#b00020;"><b>{{ fatal }}</b></p>

    {% if ddl %}
      <p class="muted">Create the table once (in Neon SQL Editor) using:</p>
      <pre style="background:#f6f6f6; padding:1rem; border-radius:10px; overflow:auto;">{{ ddl }}</pre>
    {% endif %}
    {% if hint %}
      <p class="muted">{{ hint }}</p>
    {% endif %}
    <p class="muted">After that, refresh this page.</p>
    <hr>
  {% endif %}

  {% if error %}
    <p style="color:#b00020;"><b>Error:</b> {{ error }}</p>
  {% endif %}

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

  <p><b>{{ rows|length }}</b> row(s)</p>

  <table>
    <thead>
      <tr>
        <th>ID</th><th>Name</th><th>Category</th><th>Price</th>
      </tr>
    </thead>
    <tbody>
      {% for r in rows %}
        <tr>
          <td>{{ r.get("id","") }}</td>
          <td>{{ r.get("name","") }}</td>
          <td>{{ r.get("category","") }}</td>
          <td>${{ "%.2f"|format(r.get("price",0.0)) }}</td>
        </tr>
      {% endfor %}
      {% if rows|length == 0 and not fatal %}
        <tr><td colspan="4" class="muted">No rows yet. Click “Generate Sample Data”.</td></tr>
      {% endif %}
    </tbody>
  </table>
</body>
</html>
"""


def rest_headers() -> dict:
    """
    Neon PostgREST typically expects:
      apikey: <key>
      Authorization: Bearer <key>

    If your Neon setup differs, adjust here.
    """
    if not API_KEY:
        return {"Accept": "application/json"}
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "apikey": API_KEY,
        "Authorization": f"Bearer {API_KEY}",
    }


def rest_get(path: str, params: dict | None = None) -> requests.Response:
    return requests.get(f"{BASE}{path}", headers=rest_headers(), params=params, timeout=20)


def rest_post(path: str, json_body) -> requests.Response:
    # Prefer return=representation returns inserted rows (nice for debugging)
    headers = rest_headers()
    headers["Prefer"] = "return=representation"
    return requests.post(f"{BASE}{path}", headers=headers, json=json_body, timeout=20)


def rest_delete(path: str, params: dict | None = None) -> requests.Response:
    return requests.delete(f"{BASE}{path}", headers=rest_headers(), params=params, timeout=20)


def table_missing(resp: requests.Response) -> bool:
    # PostgREST often returns 404 for unknown table/route
    return resp.status_code == 404


DDL_HINT = """CREATE TABLE IF NOT EXISTS public.furniture (
  id       BIGSERIAL PRIMARY KEY,
  name     TEXT NOT NULL UNIQUE,
  category TEXT NOT NULL DEFAULT 'General',
  price    NUMERIC(10,2) NOT NULL CHECK (price >= 0)
);"""


@app.get("/")
def index():
    # Basic connectivity check
    if not API_KEY:
        return render_template_string(
            PAGE,
            base=BASE,
            rows=[],
            error="NEON_API_KEY is not set. Set it and restart the app.",
            fatal="Missing API key.",
            ddl=DDL_HINT,
            hint="Set environment variable NEON_API_KEY, then restart.",
        )

    # Try to read the table
    resp = rest_get("/furniture", params={"select": "id,name,category,price", "order": "id.asc"})
    if table_missing(resp):
        return render_template_string(
            PAGE,
            base=BASE,
            rows=[],
            error="The /furniture endpoint was not found (table likely not created yet).",
            fatal="Furniture table not found in Postgres.",
            ddl=DDL_HINT,
            hint="Create the table once, then refresh.",
        )

    if resp.status_code >= 400:
        return render_template_string(
            PAGE,
            base=BASE,
            rows=[],
            error=f"REST error {resp.status_code}: {resp.text}",
            fatal="Could not read data from REST endpoint.",
            ddl=DDL_HINT,
            hint="Check NEON_API_KEY and that REST is enabled for this database.",
        )

    rows = resp.json() if resp.text.strip() else []
    return render_template_string(PAGE, base=BASE, rows=rows, error=request.args.get("error", ""), fatal="", ddl="", hint="")


@app.post("/seed")
def seed():
    items = [
        {"name": "Chair", "category": "Seating", "price": 39.99},
        {"name": "Table", "category": "Surface", "price": 129.00},
        {"name": "Desk", "category": "Surface", "price": 199.50},
        {"name": "Sofa", "category": "Seating", "price": 599.00},
        {"name": "Lamp", "category": "Lighting", "price": 24.95},
    ]
    resp = rest_post("/furniture", items)
    if resp.status_code >= 400:
        return redirect(url_for("index", error=f"Seed failed {resp.status_code}: {resp.text}"))
    return redirect(url_for("index"))


@app.post("/add")
def add():
    name = (request.form.get("name") or "").strip()
    category = (request.form.get("category") or "").strip() or "General"
    price_raw = (request.form.get("price") or "").strip()

    try:
        price = float(price_raw)
        if price < 0:
            raise ValueError()
    except Exception:
        return redirect(url_for("index", error="Invalid price (must be a number >= 0)."))

    resp = rest_post("/furniture", {"name": name, "category": category, "price": price})
    if resp.status_code >= 400:
        return redirect(url_for("index", error=f"Insert failed {resp.status_code}: {resp.text}"))
    return redirect(url_for("index"))


@app.post("/clear")
def clear():
    # PostgREST delete-all pattern: DELETE /table?id=gt.0 (or any always-true filter)
    resp = rest_delete("/furniture", params={"id": "gt.0"})
    if resp.status_code >= 400:
        return redirect(url_for("index", error=f"Clear failed {resp.status_code}: {resp.text}"))
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
