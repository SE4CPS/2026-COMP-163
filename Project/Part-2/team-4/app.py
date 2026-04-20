import psycopg2
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, date 

app = Flask(__name__)

# TIMESCALE = 2800 # 30 seconds = 1 day 
TIMESCALE = 1

# Database connection details

DATABASE_URL = (
    "postgresql://neondb_owner:npg_M5sVheSzQLv4@"
    "ep-shrill-tree-a819xf7v-pooler.eastus2.azure.neon.tech/"
    "neondb?sslmode=require"
)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Get all flowers
@app.route('/flowers', methods=['GET'])
def get_flowers():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT flower_id, name, last_watered, water_level, min_water_required
        FROM team4_flowers
        ORDER BY flower_id;
    """)
    flowers = cur.fetchall()

    cur.close()
    conn.close()

    now = datetime.now()

    result = []

    for f in flowers:
        elapsed_seconds = (now - f[2]).total_seconds()
        simulated_days = (elapsed_seconds / 86400) * TIMESCALE
        decay = int(simulated_days) * 5

        current_level = max(0, f[3] - decay)

        result.append({
            "id": f[0],
            "name": f[1],
            "last_watered": f[2].strftime("%Y-%m-%d"),
            "water_level": current_level,
            "min_water_required": f[4],
            "needs_watering": current_level < f[4]
        })

    return jsonify(result)
    
    # return jsonify([{
    #     "id": f[0], "name": f[1], "last_watered": f[2].strftime("%Y-%m-%d"),
    #     "water_level": f[3], "min_water_required": f[4], "needs_watering": f[3] < f[4]
    # } for f in flowers])

@app.route('/flowers/needs_watering', methods=['GET'])
def get_flowers_needing_water():
    conn = get_db_connection()
    cur = conn.cursor()
    # cur.execute("WRITE CORRECT QUERY HERE")  # Placeholder for SELECT query
    cur.execute("""
        SELECT flower_id, name, last_watered, water_level, min_water_required
        FROM team4_flowers
        WHERE water_level < min_water_required
        ORDER BY flower_id;
    """)
    flowers = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([{
        "id": f[0], "name": f[1], "last_watered": f[2].strftime("%Y-%m-%d"),
        "water_level": f[3], "min_water_required": f[4], "needs_watering": f[3] < f[4]
    } for f in flowers])

# Add a flower
@app.route('/flowers', methods=['POST'])
def add_flower():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    # cur.execute("WRITE CORRECT QUERY HERE", 
    #             (data['name'], data['last_watered'], data['water_level'], data['min_water_required']))  # Placeholder
    cur.execute("INSERT INTO team4_flowers (name, last_watered, water_level, min_water_required) VALUES (%s, %s, %s, %s)", 
                (data['name'], data['last_watered'], data['water_level'], data['min_water_required']))
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
        FROM team4_flowers
        WHERE flower_id = %s;
    """, (id,))
    stored_level, last_watered = cur.fetchone()

    now = datetime.now()

    # Apply decay logic
    elapsed_seconds = (now - datetime.combine(last_watered, datetime.min.time())).total_seconds()
    simulated_days = (elapsed_seconds / 86400) * TIMESCALE
    decay = int(simulated_days) * 5

    current_level = max(0, stored_level - decay)

    # Add new water
    new_level = current_level + data['water_level']

    # Save new base + reset time
    cur.execute("""
        UPDATE team4_flowers
        SET water_level = %s,
            last_watered = %s
        WHERE flower_id = %s;
    """, (new_level, now, id))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Flower updated successfully!"})

# Delete a flower by ID
@app.route('/flowers/<int:id>', methods=['DELETE'])
def delete_flower(id):
    conn = get_db_connection()
    cur = conn.cursor()
    # cur.execute("WRITE CORRECT QUERY HERE", (id,))  # Placeholder
    cur.execute("DELETE FROM team4_flowers WHERE flower_id =%s", (id,))  
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Flower deleted successfully!"})  

@app.route("/")
def home(): 
    return send_from_directory(".", "flowers.html")