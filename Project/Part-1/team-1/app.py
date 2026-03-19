#update
import psycopg2
from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

print("APP FILE:", __file__)
print("CURRENT DIR:", os.getcwd())
print("TEMPLATES EXISTS:", os.path.exists("templates/flowers.html"))

# Database connection details
DATABASE_URL = (
    "postgresql://neondb_owner:npg_M5sVheSzQLv4@"
    "ep-shrill-tree-a819xf7v-pooler.eastus2.azure.neon.tech/"
    "neondb?sslmode=require"
)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route('/')
def home():
    return render_template('flowers.html')

# Get all flowers
# Get all flowers
@app.route('/flowers', methods=['GET'])
def get_flowers():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            id,
            name,
            last_watered,
            GREATEST(
                water_level - (CURRENT_DATE - last_watered) * 5,
                0
            ) AS water_level,
            min_water_required
        FROM team1_flowers
    """)

    flowers = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify([{
        "id": f[0],
        "name": f[1],
        "last_watered": f[2].strftime("%Y-%m-%d"),
        "water_level": f[3],
        "needs_watering": f[3] < f[4]
    } for f in flowers])

@app.route('/flowers/needs_watering', methods=['GET'])
def get_flowers_needing_water():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM team1_flowers
        WHERE water_level < min_water_required
    """)
    flowers = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([{
        "id": f[0],
        "name": f[1],
        "last_watered": f[2].strftime("%Y-%m-%d"),
        "water_level": f[3],
        "needs_watering": f[3] < f[4]
    } for f in flowers])

# Add a flower
@app.route('/flowers', methods=['POST'])
def add_flower():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO team1_flowers (name, last_watered, water_level, min_water_required)
        VALUES (%s, %s, %s, %s)
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
        UPDATE team1_flowers
        SET last_watered = %s, water_level = %s
        WHERE id = %s
    """, (data['last_watered'], data['water_level'], id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Flower updated successfully!"})

# Water a flower
@app.route('/flowers/<int:id>/water', methods=['PUT'])
def water_flower(id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE team1_flowers
        SET water_level = water_level + 5,
            last_watered = CURRENT_DATE
        WHERE id = %s
    """, (id,))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Flower watered successfully!"})

# Delete a flower by ID
@app.route('/flowers/<int:id>', methods=['DELETE'])
def delete_flower(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM team1_flowers WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Flower deleted successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
