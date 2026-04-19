import psycopg2
from flask import Flask, request, jsonify, redirect, url_for, flash, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import admin
#NEW: added water() function
#NEW: added DATABASE_URL and get_db_connection()
#NEW: import flask.redict and flask.url_for because it is used for water()

# Database connection details
DATABASE_URL = (
    "postgresql://neondb_owner:npg_nTU5Yia7xSdB@" #"postgresql://neondb_owner:npg_M5sVheSzQLv4@"
    "ep-late-bird-amz6lx5v-pooler.c-5.us-east-1.aws.neon.tech/" #"ep-shrill-tree-a819xf7v-pooler.eastus2.azure.neon.tech/"
    "neondb?sslmode=require&channel_binding=require" #"neondb?sslmode=require"
)
def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def create_app():
    app = Flask(__name__, template_folder='template')
    admin.init_db()
    admin.seed_data()
    admin.create_indexes()
    return app

app = create_app()
app.json.sort_keys = False #Done so JSONs of SQL Queries are in original order (not auto ordered alphanumerically)
app.secret_key = "team8_secret_key"

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
#==============SQL QUERIES======================================

# Get all flowers
@app.route('/team8_flowers', methods=['GET'])
def get_flowers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, last_watered, GREATEST(water_level - (5 * (CURRENT_DATE - last_watered)),0) AS water_level, min_water_required FROM team8_flowers;") #FIXED: Changed `id` --> `flower_id`"
    
    flowers = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify([{
        "id": f[0], "name": f[1], "last_watered": f[2].strftime("%Y-%m-%d"),#FIXED: Changed `id` --> `flower_id`
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

    return jsonify([{
        "id": c[0], "name": c[1], "email": c[2]
    } for c in customers])

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

# ===FAST/SLOW QUERY ROUTES===

#Fast query of the 3 merged tables. Optimize with indexes and efficient joins.
@app.route('/team8_flowers/fast-slow_query/<int:flag>', methods=['GET'])
def fast_slow_query(flag):
    
    #if flag == 1, execute the fast query. else flag == 0, execute the slow query.
    if flag == 1:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("EXPLAIN ANALYZE SELECT id, name, last_watered, GREATEST(water_level - (5 * (CURRENT_DATE - last_watered)),0) AS water_level, min_water_required FROM team8_flowers;") 
    
        explain_analyze_info = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify([{
            "1:": f[0], "2": f[1], "3": f[2]
        } for f in explain_analyze_info])
    
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("EXPLAIN ANALYZE SELECT id, name, last_watered, GREATEST(water_level - (5 * (CURRENT_DATE - last_watered)),0) AS water_level, min_water_required FROM team8_flowers;") 

        explain_analyze_info = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify([{
            "1:": f[0], "2": f[1], "3": f[2]
        } for f in explain_analyze_info])

#==============SQL QUERIES end======================================


# Add a flower
@app.route('/team8_flowers/add', methods=['POST'])
def add_flower():
    data = request.form

    try:

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO team8_flowers (name, last_watered, water_level, min_water_required) VALUES (%s, %s, %s, %s)", 
                    (data['name'], data['last_watered'], data['water_level'], data['min_water_required'])) 
        conn.commit()
        cur.close()
        conn.close()
        flash("Flower added successfully!")
        return redirect(url_for('index'))
    
    except Exception as e:
        flash("Invalid input. Please check your values.")
        return redirect(url_for('index'))

# Update a flower by ID 
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

# Delete a flower by ID 
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

#NEW: Water
@app.route("/team8_flowers/water/<int:id>", methods=["POST"]) 
def water(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE team8_flowers
        SET water_level = GREATEST(
                water_level - (5 * (CURRENT_DATE - last_watered)),
                0
            ) + 10,
            last_watered = CURRENT_DATE
        WHERE flower_id = %s
    """, (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Flower watered successfully!")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=3000, host="0.0.0.0")