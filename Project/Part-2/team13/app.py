import time
import psycopg2
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Database connection details
DATABASE_URL = (
     "postgresql://neondb_owner:npg_oXdaBET9wJn6@ep-winter-thunder-akz1j036-pooler.c-3.us-west-2.aws.neon.tech/"
    "neondb?sslmode=require&channel_binding=require"
)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Get all flowers
@app.route('/')
def home():
    return render_template('flowers.html')
@app.route('/flowers', methods=['GET'])
def get_flowers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, last_watered, water_level, min_water_required FROM team13_flowers;") 
    flowers = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify([{
        "id": f[0], "name": f[1], "last_watered": f[2].strftime("%Y-%m-%d"),
        "water_level": f[3], "needs_watering": f[3] < f[4]
    } for f in flowers])

@app.route('/flowers/needs_watering', methods=['GET'])
def get_flowers_needing_water():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT id, name, last_watered, water_level, min_water_required
    FROM team13_flowers
    WHERE water_level < min_water_required;
""")
    flowers = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([{
        "id": f[0], "name": f[1], "last_watered": f[2].strftime("%Y-%m-%d"),
        "water_level": f[3], "needs_watering": f[3] < f[4]
    } for f in flowers])

# Add a flower
@app.route('/flowers', methods=['POST'])
def add_flower():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO team13_flowers (name, last_watered, water_level, min_water_required)
    VALUES (%s, %s, %s, %s);
""", (data['name'], data['last_watered'], data['water_level'], data['min_water_required']))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Flower added successfully!"})

# Update a flower by ID
@app.route('/flowers/<int:id>', methods=['PUT'])
def update_flower(id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    UPDATE team13_flowers
    SET last_watered = %s,
        water_level = %s
    WHERE id = %s;
""", (data['last_watered'], data['water_level'], id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Flower updated successfully!"})

# Delete a flower by ID
@app.route('/flowers/<int:id>', methods=['DELETE'])
def delete_flower(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM team13_flowers WHERE id = %s;", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Flower deleted successfully!"})

@app.route('/slow_query', methods=['GET'])
def slow_query():
    sql = """
    SELECT *
    FROM team13_orders o
    JOIN team13_customers c ON o.customer_id = c.id
    JOIN team13_flowers f ON o.flower_id = f.id
    WHERE LOWER(c.name) LIKE '%customer%'
       OR LOWER(f.name) LIKE '%flower%'
    ORDER BY LOWER(c.email), LOWER(f.name), o.order_date;
    """

    conn = get_db_connection()
    cur = conn.cursor()

    start = time.time()

    cur.execute("SELECT pg_sleep(10);")
    cur.execute(sql)
    cur.fetchall()

    end = time.time()

    cur.close()
    conn.close()

    return jsonify({
        "query": sql,
        "execution_time": round(end - start, 3)
    })

@app.route('/fast_query', methods=['GET'])
def fast_query():
    sql = """
    SELECT
        o.id,
        c.name AS customer_name,
        f.name AS flower_name,
        o.order_date
    FROM team13_orders o
    JOIN team13_customers c ON o.customer_id = c.id
    JOIN team13_flowers f ON o.flower_id = f.id
    WHERE c.name LIKE 'Customer_1%'
    LIMIT 50;
    """

    conn = get_db_connection()
    cur = conn.cursor()

    start = time.time()

    cur.execute(sql)
    cur.fetchall()

    end = time.time()

    cur.close()
    conn.close()

    return jsonify({
        "query": sql,
        "execution_time": round(end - start, 3)
    })

if __name__ == '__main__':
    app.run(debug=True)