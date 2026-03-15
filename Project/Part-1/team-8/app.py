import psycopg2
import backend
from flask import Flask, request, jsonify

app = Flask(__name__)

#Automatically update water_level on refresh is last_watered == CURRENT_DATE ?
#It will be an update with conditions?.

#ADDED this incase it was needed. 
# Database connection details
DATABASE_URL = (
    "postgresql://neondb_owner:npg_M5sVheSzQLv4@"
    "ep-shrill-tree-a819xf7v-pooler.eastus2.azure.neon.tech/"
    "neondb?sslmode=require"
)

# Get all flowers
@app.route('/team8_flowers', methods=['GET'])
def get_flowers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, lastwatered, water_level, min_water_required FROM team8_flowers")
    flowers = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify([{
        "id": f[0], "name": f[1], "last_watered": f[2].strftime("%Y-%m-%d"),
        "water_level": f[3], "needs_watering": f[3] < f[4]
    } for f in flowers])

@app.route('/team8_flowers/needs_water', methods=['GET'])
def get_flowers_needing_water():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, lastwatered, water_level, min_water_required FROM team8_flowers WHERE (water_level < min_water_required)")  # Placeholder for SELECT query
    flowers = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([{
        "id": f[0], "name": f[1], "last_watered": f[2].strftime("%Y-%m-%d"),
        "water_level": f[3], "needs_watering": f[3] < f[4]
    } for f in flowers])

# Add a flower
@app.route('/team8_flowers/add', methods=['POST'])
def add_flower():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO team8_flowers (name, last_watered, water_level, min_water_required) VALUES (%s, %s, %s, %s)", 
                (data['name'], data['last_watered'], data['water_level'], data['min_water_required'])) 
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Flower added successfully!"})

# Update a flower by ID
@app.route('/team8_flowers/update/<int:id>', methods=['PUT'])
def update_flower(id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE team8_flowers SET name = %s, last_watered = %s, water_level = %s WHERE id = %s;", 
                (data['last_watered'], data['water_level'], id)) 
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Flower updated successfully!"})

# Delete a flower by ID
@app.route('/team8_flowers/delete/<int:id>', methods=['DELETE'])
def delete_flower(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM team8_flowers WHERE id = %s", (id,)) 
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Flower deleted successfully!"})  

#NEW: Added water
@app.route("/team8_flowers/water/<int:id>", methods=["POST"])
def water(flower_id):
    backend.water_flower(flower_id)
    return redirect(url_for("frontend.index"))