import psycopg2
import backend
from flask import Flask, request, jsonify
from flask import redirect, url_for, flash
#NEW: added water() function
#NEW: added DATABASE_URL and get_db_connection()
#NEW: import flask.redict and flask.url_for because it is used for water()

# Database connection details
DATABASE_URL = (
    "postgresql://neondb_owner:npg_M5sVheSzQLv4@"
    "ep-shrill-tree-a819xf7v-pooler.eastus2.azure.neon.tech/"
    "neondb?sslmode=require"
)
def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

app = Flask(__name__, template_folder='template')
app.json.sort_keys = False #Done so JSONs of SQL Queries are in original order (not auto ordered alphanumerically)
app.secret_key = "team8_secret_key"
# #Starting page 
# @app.route('/')
# def test_home():
#     return "Flower Watering App"
from flask import render_template
#Starting page 
@app.route('/')
def index():
    return render_template('flower.html')

#Column page for testing our column labels. #WE NEEDED TO USE `flower_id` the entire time!!!! not `id`
@app.route('/column-name')
def get_columns():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'team8_flowers';
    """)
    flowers = cur.fetchall()
    cur.close()
    conn.close()
    return flowers
#==============SQL QUERIES==============

# Get all flowers
@app.route('/team8_flowers', methods=['GET'])
def get_flowers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT flower_id, name, last_watered, water_level, min_water_required FROM team8_flowers") #FIXED: Changed `id` --> `flower_id`
    flowers = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify([{
        "flower_id": f[0], "name": f[1], "last_watered": f[2].strftime("%Y-%m-%d"),#FIXED: Changed `id` --> `flower_id`
        "water_level": f[3], "min_water_required": f[4], "needs_watering": f[3] < f[4]
    } for f in flowers])

#Get flowers needing water
@app.route('/team8_flowers/needs_water', methods=['GET'])
def get_flowers_needing_water():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT flower_id, name, last_watered, water_level, min_water_required FROM team8_flowers WHERE (water_level < min_water_required)")  #FIXED: Changed `id` --> `flower_id` and `lastwatered` --> `last_watered`
    flowers = cur.fetchall()
    cur.close()
    conn.close()

    #FIXED: Changed `id` --> `flower_id`
    return jsonify([{
        "flower_id": f[0], "name": f[1], "last_watered": f[2].strftime("%Y-%m-%d"),  
        "water_level": f[3], "needs_watering": f[3] < f[4]
    } for f in flowers])
    

# Add a flower -- WORKING -----------------------
@app.route('/team8_flowers/add', methods=['POST'])
def add_flower():
    data = request.form
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO team8_flowers (name, last_watered, water_level, min_water_required) VALUES (%s, %s, %s, %s)", 
                (data['name'], data['last_watered'], data['water_level'], data['min_water_required'])) 
    conn.commit()
    cur.close()
    conn.close()
    flash("Flower added successfully!")
    return redirect(url_for('index'))

# Update a flower by ID -- NOT WORKING-------------
#I think this should also be part of the frontend buttons or inputs? Let someone edit a flower based on a flower_id ???
@app.route('/team8_flowers/update/<int:id>', methods=['POST'])
def update_flower(id):
    data = request.form

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE team8_flowers SET name = %s, last_watered = %s, water_level = %s, min_water_required = %s WHERE flower_id = %s;", #FIXED: Changed `id` --> `flower_id`
                (data['name'], data['last_watered'], data['water_level'], data['min_water_required'], data['id'])) 
    conn.commit()
    cur.close()
    conn.close()
    flash("Flower updated successfully!")
    return redirect(url_for('index'))

# Delete a flower by ID -- NOT WORKING ------------
@app.route('/team8_flowers/delete/<int:id>', methods=['POST'])
def delete_flower(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM team8_flowers WHERE flower_id = %s", (id,)) #FIXED: Changed `id` --> `flower_id`
    conn.commit()
    cur.close()
    conn.close()
    flash("Flower deleted successfully!")
    return redirect(url_for('index'))

#NEW: Water  NOT TESTED ------------
@app.route("/team8_flowers/water/<int:id>", methods=["POST"]) 
def water(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE team8_flowers
        SET water_level = water_level + 10,
            last_watered = CURRENT_DATE
        WHERE flower_id = %s;
    """, (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Flower watered successfully!")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=3000, host="0.0.0.0")