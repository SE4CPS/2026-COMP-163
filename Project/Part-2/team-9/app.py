import psycopg2
from flask import Flask, request, jsonify, send_file
from db_conn import DATABASE_URL

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Get all flowers
@app.route('/flowers', methods=['GET'])
def get_flowers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, last_watered, water_level, min_water_required FROM team9_flowers;")
    flowers = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify([{
        "id": f[0], "name": f[1], "last_watered": f[2].strftime("%Y-%m-%d"),
        "water_level": f[3], "needs_watering": f[3] < f[4], "min_water_required": f[4]
    } for f in flowers])

@app.route('/flowers/needs_watering', methods=['GET'])
def get_flowers_needing_water():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM team9_flowers
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
        INSERT INTO team9_flowers (name, last_watered, water_level, last_watered_water_level, min_water_required)
        VALUES (%s, %s, %s, %s, %s);
    """, (data['name'], data['last_watered'], data['water_level'], data['water_level'], data['min_water_required']))
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
        UPDATE team9_flowers
        SET last_watered = %s,
            water_level = %s,
            last_watered_water_level = %s
        WHERE id = %s;
    """, (data['last_watered'], data['water_level'], data['water_level'], id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Flower updated successfully!"})

# Water a flower by ID
@app.route('/flowers/water/<int:id>', methods=['PUT'])
def water_flower(id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE team9_flowers
        SET last_watered = CURRENT_DATE,
            water_level = %s,
            last_watered_water_level = %s
        WHERE id = %s;
    """, (data['water_level'], data['water_level'], id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Flower updated successfully!"})

# Delete a flower by ID
@app.route('/flowers/<int:id>', methods=['DELETE'])
def delete_flower(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM team9_flowers
        WHERE id = %s;
    """, (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Flower deleted successfully!"})  

# slow query (part 2)
@app.route('/slow_query', methods=['GET'])
def slow_query():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id, c.name, c.email, o.id, o.order_date, f.id, f.name, o.customer_id, o.flower_id
        FROM team9_orders o
        CROSS JOIN team9_customers c
        CROSS JOIN team9_flowers f;
    """)

    results = cur.fetchall()
    orders = []
    for customer_id, customer_name, customer_email, order_id, order_date, flower_id, flower_name, order_customer_id, order_flower_id in results:
        if flower_id != order_flower_id or customer_id != order_customer_id:
            continue

        order = {
            "customer_id": customer_id, 
            "customer_name": customer_name, 
            "customer_email": customer_email, 
            "order_id": order_id, 
            "order_date": order_date, 
            "flower_id": flower_id, 
            "flower_name": flower_name, 
        }

        print(order)
        orders.append(order)

    cur.close()
    conn.close()
    return jsonify(orders)

# slow query (part 2)
@app.route('/optimized_query', methods=['GET'])
def optimized_query():
    conn = get_db_connection()
    cur = conn.cursor()

    # TODO: further optimization
    cur.execute("""
        SELECT c.id, c.name, c.email, o.id, o.order_date, f.id, f.name
        FROM team9_orders o
        CROSS JOIN team9_customers c
        CROSS JOIN team9_flowers f
        WHERE o.customer_id = c.id AND o.flower_id = f.id;
    """)

    results = cur.fetchall()
    orders = []
    for customer_id, customer_name, customer_email, order_id, order_date, flower_id, flower_name in results:

        order = {
            "customer_id": customer_id, 
            "customer_name": customer_name, 
            "customer_email": customer_email, 
            "order_id": order_id, 
            "order_date": order_date, 
            "flower_id": flower_id, 
            "flower_name": flower_name, 
        }

        print(order)
        orders.append(order)

    cur.close()
    conn.close()
    return jsonify(orders)


@app.route('/')
def home():
    return send_file('flowers.html')
