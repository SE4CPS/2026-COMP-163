import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database connection details ADDED
DATABASE_URL = (
    "postgresql://neondb_owner:npg_M5sVheSzQLv4@"
    "ep-shrill-tree-a819xf7v-pooler.eastus2.azure.neon.tech/"
    "neondb?sslmode=require"
)

# create a color indicator function for is the flower needs watering later
# GREEN - no watering needed
# YELLOW - may need watering soon
# RED - needs to be watered now

# Get all flowers
@app.route('/flowers', methods=['GET'])
def get_flowers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, lastwatered, water_level, min_water_required" \
                "FROM team5_flowers;")  # Placeholder for SELECT query (used SELECT and FROM)
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
    cur.execute("SELECT id, name, last_watered, water_level, min_water_required" \
                "FROM team5_flowers" \
                "WHERE water_level < min_water_required")  # Placeholder for SELECT query (used WHERE to see if flower needs watering)
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
    cur.execute("INSERT INTO team5_flowers (name, last_watered, water_level, min_water_required)" \
                "VALUES (%s, %s, %s, %s);", # how to make place holders
                (data['name'], data['last_watered'], data['water_level'], data['min_water_required']))  # Placeholder
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
    cur.execute("UPDATE team5_flowers" \
                "SET last_watered = %s," \
                    " water_level = %s" \
                "WHERE id = %s;", 
                (data['last_watered'], data['water_level'], id))  # Placeholder
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Flower updated successfully!"})

# Delete a flower by ID
@app.route('/flowers/<int:id>', methods=['DELETE'])
def delete_flower(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM team5_flowers" \
                "WHERE id = %s", (id,))  # Placeholder
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Flower deleted successfully!"})

# Water a Flower (watering algorithm)
# # Use this algorithm provided
    # UPDATE teamX_flowers
    # SET water_level = water_level - (5 * (CURRENT_DATE - last_watered));
# use PUT methods ???