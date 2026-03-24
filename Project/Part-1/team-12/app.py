import psycopg2
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# Database connection details
DATABASE_URL = (
    "postgresql://neondb_owner:npg_M5sVheSzQLv4@"
    "ep-shrill-tree-a819xf7v-pooler.eastus2.azure.neon.tech/"
    "neondb?sslmode=require"
)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

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

    cur.execute("""
        UPDATE team12_flowers
        SET water_level = %s, last_watered = %s
        WHERE id = %s
    """, (new_water_level, new_last_watered, id))  # query to update flower details
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Flower updated successfully!"})

# Delete a flower by ID
@app.route('/flowers/<int:id>', methods=['DELETE'])
def delete_flower(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM team12_flowers WHERE id = %s", (id,))  # Placeholder
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Flower deleted successfully!"})  

@app.route("/")
def home(): 
    return send_from_directory(".", "flowers.html")