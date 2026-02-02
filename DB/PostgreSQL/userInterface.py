from flask import Flask, request, redirect, url_for, render_template_string
import psycopg2

app = Flask(__name__)

# Neon PostgreSQL connection string
DATABASE_URL = (
    "postgresql://neondb_owner:npg_M5sVheSzQLv4@"
    "ep-shrill-tree-a819xf7v-pooler.eastus2.azure.neon.tech/"
    "neondb?sslmode=require"
)

# ---------- DB helpers ----------

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Furniture (
            furniture_id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL DEFAULT 'General',
            price NUMERIC(10,2) NOT NULL CHECK (price >= 0)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def seed_data():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Furniture (name, category, price)
        VALUES
            ('Chair', 'Seating', 39.99),
            ('Table', 'Surface', 129.00),
            ('Desk', 'Surface', 199.50)
        ON CONFLICT (name) DO NOTHING;
    """)
    conn.commit()
    cur.close()
    conn.close()

# ---------- Simple HTML template ----------

PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Furniture CRUD (PostgreSQL)</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; }
    th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
    th { background: #f3f3f3; }
    form { margin: 0; }
    .row { display:flex; gap:12px; flex-wrap:wrap; }
    .card { border:1px solid #ddd; padding:12px; border-radius:8px; margin-bottom:16px; }
    input { padding:6px; }
    button { padding:6px 10px; cursor:pointer; }
    .muted { color:#666; font-size:0.9em; }
  </style>
</head>
<body>
  <h2>Furniture CRUD (PostgreSQL / Neon)</h2>
  <p class="muted">Routes: <code>/</code> list • <code>/add</code> create • <code>/edit/&lt;id&gt;</code> update • <code>/delete/&lt;id&gt;</code> delete</p>

  <div class="card">
    <h3>Add Furniture</h3>
    <form method="POST" action="{{ url_for('add') }}">
      <div class="row">
        <label>Name<br><input name="name" required></label>
        <label>Category<br><input name="category" placeholder="General"></label>
        <label>Price<br><input name="price" type="number" step="0.01" min="0" required></label>
        <div style="align-self:end;"><button type="submit">Add</button></div>
      </div>
    </form>
  </div>

  {% if edit_item %}
  <div class="card">
    <h3>Edit Furniture #{{ edit_item.furniture_id }}</h3>
    <form method="POST" action="{{ url_for('edit', furniture_id=edit_item.furniture_id) }}">
      <div class="row">
        <label>Name<br><input name="name" value="{{ edit_item.name }}" required></label>
        <label>Category<br><input name="category" value="{{ edit_item.category }}" required></label>
        <label>Price<br><input name="price" type="number" step="0.01" min="0" value="{{ edit_item.price }}" required></label>
        <div style="align-self:end;">
          <button type="submit">Save</button>
          <a href="{{ url_for('index') }}" style="margin-left:10px;">Cancel</a>
        </div>
      </div>
    </form>
  </div>
  {% endif %}

  <h3>Furniture Table</h3>
  <table>
    <thead>
      <tr>
        <th>ID</th><th>Name</th><th>Category</th><th>Price</th><th>Actions</th>
      </tr>
    </thead>
    <tbody>
      {% for r in rows %}
      <tr>
        <td>{{ r.furniture_id }}</td>
        <td>{{ r.name }}</td>
        <td>{{ r.category }}</td>
        <td>{{ r.price }}</td>
        <td>
          <a href="{{ url_for('index', edit=r.furniture_id) }}">Edit</a>
          &nbsp;|&nbsp;
          <form method="POST" action="{{ url_for('delete', furniture_id=r.furniture_id) }}" style="display:inline;">
            <button type="submit" onclick="return confirm('Delete this item?');">Delete</button>
          </form>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""

# ---------- Routes ----------

@app.route("/")
def index():
    init_db()
    seed_data()

    edit_id = request.args.get("edit")
    edit_item = None

    conn = get_conn()
    cur = conn.cursor()

    if edit_id:
        cur.execute(
            "SELECT furniture_id, name, category, price FROM Furniture WHERE furniture_id = %s;",
            (edit_id,)
        )
        row = cur.fetchone()
        if row:
            edit_item = {
                "furniture_id": row[0],
                "name": row[1],
                "category": row[2],
                "price": row[3],
            }

    cur.execute("SELECT furniture_id, name, category, price FROM Furniture ORDER BY furniture_id;")
    rows_raw = cur.fetchall()
    cur.close()
    conn.close()

    rows = [
        {"furniture_id": r[0], "name": r[1], "category": r[2], "price": r[3]}
        for r in rows_raw
    ]

    return render_template_string(PAGE, rows=rows, edit_item=edit_item)

@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "").strip()
    category = (request.form.get("category", "").strip() or "General")
    price = request.form.get("price", "").strip()

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO Furniture (name, category, price) VALUES (%s, %s, %s);",
            (name, category, price)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        # Minimal: show error in terminal, keep app running
        print("Add error:", e)
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("index"))

@app.route("/edit/<int:furniture_id>", methods=["POST"])
def edit(furniture_id):
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    price = request.form.get("price", "").strip()

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE Furniture SET name=%s, category=%s, price=%s WHERE furniture_id=%s;",
            (name, category, price, furniture_id)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Edit error:", e)
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("index"))

@app.route("/delete/<int:furniture_id>", methods=["POST"])
def delete(furniture_id):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Furniture WHERE furniture_id=%s;", (furniture_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Delete error:", e)
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("index"))

if __name__ == "__main__":
    # Run: python app.py
    app.run(debug=True)
