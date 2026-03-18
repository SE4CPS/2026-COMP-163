from flask import Flask, request, jsonify

import admin
import backend


app = Flask(__name__)

# Initialize DB schema + seed sample rows (as required by the template).
admin.init_db()
admin.seed_data()


@app.route("/flowers", methods=["GET"])
def get_flowers():
    flowers = backend.get_flowers_api(needs_only=False)
    return jsonify(flowers)


@app.route("/flowers/needs_watering", methods=["GET"])
def get_flowers_needing_water():
    flowers = backend.get_flowers_api(needs_only=True)
    return jsonify(flowers)


@app.route("/flowers", methods=["POST"])
def add_flower():
    data = request.get_json(force=True)
    required = ["name", "last_watered", "water_level", "min_water_required"]
    for k in required:
        if k not in data:
            return jsonify({"message": f"Missing field: {k}"}), 400

    new_id = backend.add_flower_api(
        name=data["name"],
        last_watered=data["last_watered"],
        water_level=data["water_level"],
        min_water_required=data["min_water_required"],
    )
    if new_id is None:
        return jsonify({"message": "Flower added failed"}), 400

    return jsonify({"message": "Flower added successfully!", "id": new_id}), 201


@app.route("/flowers/<int:id>", methods=["PUT"])
def update_flower(id):
    data = request.get_json(force=True)
    if "last_watered" not in data or "water_level" not in data:
        return jsonify({"message": "Missing fields: last_watered, water_level"}), 400

    min_water_required = data.get("min_water_required")
    ok = backend.update_flower_api(
        id=id,
        last_watered=data["last_watered"],
        water_level=data["water_level"],
        min_water_required=min_water_required,
    )
    if not ok:
        return jsonify({"message": "Flower not found"}), 404

    return jsonify({"message": "Flower updated successfully!"})


@app.route("/flowers/<int:id>", methods=["DELETE"])
def delete_flower(id):
    ok = backend.delete_flower_api(id=id)
    if not ok:
        return jsonify({"message": "Flower not found"}), 404

    return jsonify({"message": "Flower deleted successfully!"})


if __name__ == "__main__":
    # Run on 5001 to match the assignment’s typical setup.
    app.run(host="127.0.0.1", port=5001, debug=True)

