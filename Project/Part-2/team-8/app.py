import time
import psycopg2
from flask import Flask, request, jsonify, redirect, url_for, flash, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import admin

# Database connection details
DATABASE_URL = (
    "postgresql://neondb_owner:npg_nTU5Yia7xSdB@"
    "ep-late-bird-amz6lx5v-pooler.c-5.us-east-1.aws.neon.tech/"
    "neondb?sslmode=require&channel_binding=require"
)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def create_app():
    app = Flask(__name__, template_folder='template')
    admin.init_db()
    admin.seed_data()
    admin.create_indexes()   # Part 2: indexes used by the fast query
    return app

app = create_app()
app.json.sort_keys = False
app.secret_key = "team8_secret_key"


# ============================================================
# Part 2 Query Texts
# ============================================================
# Kept as module-level strings so the /slow_query and /fast_query
# endpoints can both execute them AND return the SQL text to the
# frontend (to display next to each button).

SLOW_SQL = """
SELECT *
FROM team8_orders o, team8_customers c, team8_flowers f
WHERE CAST(o.customer_id AS TEXT) = CAST(c.id AS TEXT)
  AND CAST(o.flower_id   AS TEXT) = CAST(f.id AS TEXT)
  AND LOWER(c.email) LIKE '%customer%'
  AND LOWER(c.name)  LIKE '%customer%'
  AND UPPER(f.name)  LIKE '%O%'
  AND md5(c.name || c.email || f.name || o.order_date::text) LIKE '%a%'
ORDER BY md5(c.email || c.name || f.name || o.order_date::text),
         LOWER(c.name),
         UPPER(f.name),
         md5(o.order_date::text);
""".strip()

FAST_SQL = """
SELECT o.id AS order_id,
       o.order_date,
       c.name  AS customer_name,
       c.email AS customer_email,
       f.name  AS flower_name
FROM team8_orders   o
JOIN team8_customers c ON o.customer_id = c.id
JOIN team8_flowers   f ON o.flower_id   = f.id
WHERE f.name IN ('Rose', 'Poppy')
  AND c.email LIKE 'customer_%'
ORDER BY o.id
LIMIT 100 OFFSET 0;
""".strip()


def _run_and_time(sql: str):
    """Execute a SQL string, discard the rows, return elapsed seconds.
    Matches the spirit of \\timing on / \\timing off."""
    conn = get_db_connection()
    cur  = conn.cursor()
    start = time.perf_counter()
    cur.execute(sql)
    try:
        cur.fetchall()          # consume so network + serialization time counts
    except psycopg2.ProgrammingError:
        pass                    # no results to fetch (shouldn't happen here)
    elapsed = time.perf_counter() - start
    cur.close()
    conn.close()
    return elapsed


# ------------------ Pages ------------------
@app.route('/')
def index():
    return render_template('flower.html')


# ------------------ Part 1 CRUD endpoints (unchanged) ------------------
@app.route('/team8_flowers', methods=['GET'])
def get_flowers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, last_watered,
               GREATEST(water_level - (5 * (CURRENT_DATE - last_watered)), 0) AS water_level,
               min_water_required
        FROM team8_flowers;
    """)
    flowers = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{
        "id": f[0], "name": f[1], "last_watered": f[2].strftime("%Y-%m-%d"),
        "water_level": f[3], "min_water_required": f[4], "needs_watering": f[3] < f[4]
    } for f in flowers])


@app.route('/team8_customers', methods=['GET'])
def get_customers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM team8_customers LIMIT 10;")
    customers = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"id": c[0], "name": c[1], "email": c[2]} for c in customers])


@app.route('/team8_flowers/needs_water', methods=['GET'])
def get_flowers_needing_water():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, last_watered, water_level, min_water_required
        FROM team8_flowers
        WHERE water_level < min_water_required;
    """)
    flowers = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{
        "id": f[0], "name": f[1], "last_watered": f[2].strftime("%Y-%m-%d"),
        "water_level": f[3], "needs_watering": f[3] < f[4]
    } for f in flowers])


# ============================================================
# Part 2: Slow Query and Fast Query endpoints
# ============================================================
# Each endpoint runs its query, times it, and returns:
#   { "sql": <query text>, "execution_time_seconds": <float> }
# It deliberately does NOT return the rows (per spec 3.3).

@app.route('/team8_flowers/slow_query', methods=['GET'])
def slow_query():
    elapsed = _run_and_time(SLOW_SQL)
    return jsonify({
        "label": "Slow Query",
        "sql": SLOW_SQL,
        "execution_time_seconds": round(elapsed, 3)
    })


@app.route('/team8_flowers/fast_query', methods=['GET'])
def fast_query():
    elapsed = _run_and_time(FAST_SQL)
    return jsonify({
        "label": "Fast Query",
        "sql": FAST_SQL,
        "execution_time_seconds": round(elapsed, 3)
    })


# Optional: admin endpoints so you can re-demo the slow case
# by dropping indexes, and re-enable them again.
@app.route('/team8_flowers/indexes/create', methods=['POST'])
def indexes_create():
    admin.create_indexes()
    return jsonify({"status": "indexes created"})

@app.route('/team8_flowers/indexes/drop', methods=['POST'])
def indexes_drop():
    admin.drop_indexes()
    return jsonify({"status": "indexes dropped"})


# ------------------ Part 1 write endpoints (unchanged behavior) ------------------
@app.route('/team8_flowers/add', methods=['POST'])
def add_flower():
    data = request.form
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO team8_flowers (name, last_watered, water_level, min_water_required) VALUES (%s, %s, %s, %s)",
            (data['name'], data['last_watered'], data['water_level'], data['min_water_required'])
        )
        conn.commit()
        cur.close()
        conn.close()
        flash("Flower added successfully!")
        return redirect(url_for('index'))
    except Exception:
        flash("Invalid input. Please check your values.")
        return redirect(url_for('index'))


@app.route('/team8_flowers/update/<int:id>', methods=['POST'])
def update_flower(id):
    data = request.form
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE team8_flowers SET name = %s, last_watered = %s, water_level = %s, min_water_required = %s WHERE id = %s;",
        (data['name'], data['last_watered'], data['water_level'], data['min_water_required'], id)
    )
    conn.commit()
    cur.close()
    conn.close()
    flash("Flower updated successfully!")
    return redirect(url_for('index'))


@app.route('/team8_flowers/delete/<int:id>', methods=['POST'])
def delete_flower(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM team8_flowers WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Flower deleted successfully!")
    return redirect(url_for('index'))


@app.route("/team8_flowers/water/<int:id>", methods=["POST"])
def water(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE team8_flowers
        SET water_level = GREATEST(water_level - (5 * (CURRENT_DATE - last_watered)), 0) + 10,
            last_watered = CURRENT_DATE
        WHERE id = %s
    """, (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Flower watered successfully!")
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=3000, host="0.0.0.0")