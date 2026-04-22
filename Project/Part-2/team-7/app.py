import psycopg2
from flask import request, jsonify
import admin
import time

DATABASE_URL = (
    "postgresql://neondb_owner:npg_XUjioFP10Nyk@ep-empty-mud-anusqxyo-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def apply_watering_loss():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE team7_flowers
        SET water_level = GREATEST(
            0,
            water_level - (5 * (CURRENT_DATE - last_watered))
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def register_routes(bp):
    @bp.route('/flowers', methods=['GET'])
    def get_flowers():
        apply_watering_loss()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, last_watered, water_level, min_water_required
            FROM team7_flowers
            ORDER BY id;
        """)
        flowers = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify([{
            "id": f[0],
            "name": f[1],
            "last_watered": f[2].strftime("%Y-%m-%d"),
            "water_level": f[3],
            "min_water_required": f[4],
            "needs_watering": f[3] < f[4]
        } for f in flowers])

    @bp.route('/flowers/needs_watering', methods=['GET'])
    def get_flowers_needing_water():
        apply_watering_loss()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, last_watered, water_level, min_water_required
            FROM team7_flowers
            WHERE water_level < min_water_required
            ORDER BY id;
        """)
        flowers = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify([{
            "id": f[0],
            "name": f[1],
            "last_watered": f[2].strftime("%Y-%m-%d"),
            "water_level": f[3],
            "min_water_required": f[4],
            "needs_watering": f[3] < f[4]
        } for f in flowers])

    @bp.route('/flowers', methods=['POST'])
    def add_flower():
        data = request.json

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO team7_flowers (name, last_watered, water_level, min_water_required)
            VALUES (%s, %s, %s, %s);
        """, (
            data['name'],
            data['last_watered'],
            data['water_level'],
            data['min_water_required']
        ))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Flower added successfully!"})

    @bp.route('/flowers/<int:id>', methods=['PUT'])
    def update_flower(id):
        data = request.json

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE team7_flowers
            SET last_watered = %s,
                water_level = %s
            WHERE id = %s;
        """, (
            data['last_watered'],
            data['water_level'],
            id
        ))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Flower updated successfully!"})

    @bp.route('/flowers/<int:id>', methods=['DELETE'])
    def delete_flower(id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM team7_flowers
            WHERE id = %s;
        """, (id,))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Flower deleted successfully!"})

    @bp.route('/benchmark/slow', methods=['GET'])
    def run_slow_query():
        started = time.time()
        result = admin.slow_query()
        end_to_end = time.time() - started

        return jsonify({
            "query_type": "slow",
            "sql": result["sql"],
            "db_time_seconds": result["elapsed_seconds"],
            "end_to_end_seconds": round(end_to_end, 4)
        })

    @bp.route('/benchmark/fast', methods=['GET'])
    def run_fast_query():
        started = time.time()
        result = admin.fast_query()
        end_to_end = time.time() - started

        return jsonify({
            "query_type": "fast",
            "sql": result["sql"],
            "db_time_seconds": result["elapsed_seconds"],
            "end_to_end_seconds": round(end_to_end, 4)
        })
