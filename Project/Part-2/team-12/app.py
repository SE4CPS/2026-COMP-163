import time
import psycopg2
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# Database connection details
DATABASE_URL = (
    "postgresql://neondb_owner:npg_7Wbwi6IhVnou"
    "@ep-patient-silence-a4j19orv-pooler.us-east-1.aws.neon.tech"
    "/neondb?sslmode=require&channel_binding=require"
)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route('/performance/slow_query', methods=['GET'])
def slow_query():
    conn = get_db_connection()
    cur = conn.cursor()

    start_timer = time.time()
    # cur.execute("""
    #     SELECT 
    #         o.id,
    #         o.order_date,
    #         c.name,
    #         c.email,
    #         f.name AS flower_name
    #     FROM team12_orders o
    #     JOIN team12_customers c ON o.customer_id = c.id
    #     JOIN team12_flowers f ON o.flower_id = f.id
    #     WHERE LOWER(c.name) LIKE '%customer%'
    #     ORDER BY LOWER(f.name), LOWER(c.name), o.order_date DESC
    # """)
    cur.execute("""
        SELECT
            c.name,
            c.email,
            f.name,
            o.order_date
        FROM team12_orders o
        JOIN team12_customers c ON o.customer_id = c.id
        JOIN team12_flowers f   ON o.flower_id = f.id
        CROSS JOIN generate_series(1, 35) AS n
        WHERE LOWER(c.name) LIKE '%customer%'
        ORDER BY LOWER(f.name), LOWER(c.name), o.order_date DESC;
    """)
    rows = cur.fetchall()
    time_elapsed = time.time() - start_timer

    cur.close()
    conn.close()
    return jsonify({
        "query_time_seconds": time_elapsed,
        "rows_returned": len(rows),
        # "results": [{
        #     "order_id": row[0],
        #     "customer": row[1],
        #     "email":    row[2],
        #     "flower":   row[3],
        #     "date":     row[4].strftime("%Y-%m-%d")
        # } for row in rows]
    })

@app.route('/performance/fast_query', methods=['GET'])
def fast_query():
    conn = get_db_connection()
    cur = conn.cursor()

    start_timer = time.time()
    cur.execute("""
        SELECT
            o.id,
            o.order_date,
            c.name,
            c.email,
            f.name AS flower_name
        FROM team12_orders o
        JOIN team12_customers c ON o.customer_id = c.id
        JOIN team12_flowers f ON o.flower_id = f.id
        WHERE  c.name LIKE 'Customer_%'
        ORDER  BY c.name, o.order_date DESC
        LIMIT  50 OFFSET 0
    """)
    rows = cur.fetchall()
    time_elapsed = time.time() - start_timer
    cur.close()
    conn.close()
    return jsonify({
        "query_time_seconds": time_elapsed,
        "rows_returned": len(rows),
        # "results": [{
        #     "order_id": row[0],
        #     "date":     row[1].strftime("%Y-%m-%d"),
        #     "customer": row[2],
        #     "email":    row[3],
        #     "flower":   row[4]
        # } for row in rows]
    })


# Simulate daily water loss (5 inches per day since last watered)
@app.route('/flowers/simulate', methods=['POST'])
def simulate_water_loss():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE team12_flowers
        SET water_level = water_level - (5 * (CURRENT_DATE - last_watered));
    """)
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Water loss simulated successfully!"})

# Get all flowers
@app.route('/flowers', methods=['GET'])
def get_flowers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM team12_flowers
        ORDER BY id;
    """)  # SELECT query
    flowers = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify([{
        "id": f[0], "name": f[1], "last_watered": f[2].strftime("%Y-%m-%d"),
        "water_level": f[3], "min_water_required": f[4], "needs_watering": f[3] < f[4]
    } for f in flowers])

@app.route('/flowers/needs_watering', methods=['GET'])
def get_flowers_needing_water():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM team12_flowers
        WHERE water_level < min_water_required
        ORDER BY id;
    """)  # SELECT query
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
    cur.execute("INSERT INTO team12_flowers (name, last_watered, water_level, min_water_required) VALUES (%s, %s, %s, %s)", 
                (data['name'], data['last_watered'], data['water_level'], data['min_water_required'])) # query to insert a new flower
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

    # Get current stored values
    cur.execute("""
        SELECT water_level, last_watered
        FROM team12_flowers
        WHERE id = %s
    """, (id,))
    current_data = cur.fetchone()
    if not current_data:
        cur.close()
        conn.close()
        return jsonify({"message": "Flower not found!"}), 404

    current_water_level, current_last_watered = current_data

    # Update values based on input, keeping existing values if not provided
    new_water_level = current_water_level + data.get('water_level', 0)
    new_last_watered = data.get('last_watered', current_last_watered)

    # query to update flower details
    cur.execute("""
        UPDATE team12_flowers
        SET water_level = %s, last_watered = %s
        WHERE id = %s
    """, (new_water_level, new_last_watered, id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Flower updated successfully!"})

# Delete a flower by ID
@app.route('/flowers/<int:id>', methods=['DELETE'])
def delete_flower(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM team12_flowers WHERE id = %s", (id,))  # query to delete a flower by ID
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Flower deleted successfully!"})  

@app.route("/")
def home(): 
    return send_from_directory(".", "flowers.html")