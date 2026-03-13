from flask import Blueprint, request, redirect, url_for, render_template_string
import backend
import app

frontend_bp = Blueprint("frontend", __name__)

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Flower Watering Status</title>
</head>

<h2>Flower Watering Status</h2>

<div class="card" style="margin-top: 14px;">
      <h3>Add Flower</h3>
      <form method="post" action="/add">
        <label>Flower name</label>
        <input name="name" placeholder="e.g., Azalea" required /> <br>
        <label>Last watered</label>
        <input name="last_watered" placeholder = "e.g., 2026-03-13" required/> <br>
        <label>Water level</label>
        <input name="water_level" placeholder = "e.g., 10" required/> <br>
        <label>Minimum water required</label>
        <input name="min_water_required" placeholder = "e.g., 7" required/> <br>
        <button type="submit">Add Flower</button>
      </form>
</div>

<table border="1">
    <br>
    <tr>
        <th>Name</th>
        <th>Last Watered</th>
        <th>Water Level</th>
        <th>Needs Watering</th>
        <th>Action</th>
    </tr>



    <tbody>
    {% for flower in rows %}
    <tr>
        <td>{{ flower.name }}</td>
        <td>{{ flower.last_watered }}</td>
        <td>{{ flower.water_level }} inches</td>
        <td>
            {% if flower.water_level < flower.min_water_required %}
                Yes
            {% else %}
                No
            {% endif %}
        </td>
        <td>   
            <form method="POST" action="/water/{{ flower.flower_id }}">
            <button type="submit">Water</button>
            </form>
        </td>

        <td>   
            <form method="POST" action="/delete/{{ flower.flower_id }}" style="margin:0;">
            <button type="submit">Delete</button>
            </form>
        </td>
    </tr>
    {% endfor %}
    </tbody>
</table>
</html>
"""


@frontend_bp.route("/")
def index():
    edit_id = request.args.get("edit", type=int)
    edit_item = backend.select_flower(edit_id) if edit_id else None
    rows = backend.select_flower(None)
    return render_template_string(PAGE, rows=rows, edit_item=edit_item)

@frontend_bp.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "").strip()
    last_watered = request.form.get("last_watered", "").strip()
    water_level = request.form.get("water_level", "").strip()
    min_water_required = request.form.get("min_water_required", "").strip()
    backend.insert_flower(name,last_watered, water_level, min_water_required)
    return redirect(url_for("frontend.index"))

@frontend_bp.route("/edit/<int:flower_id>", methods=["POST"])
def edit(flower_id):
    name = request.form.get("name", "").strip()
    last_watered = request.form.get("last_watered", "").strip()
    water_level = request.form.get("water_level", "").strip()
    min_water_required = request.form.get("min_water_required", "").strip()
    backend.update_flower(flower_id,name,last_watered, water_level, min_water_required)
    return redirect(url_for("frontend.index"))

@frontend_bp.route("/delete/<int:flower_id>", methods=["POST"])
def delete(flower_id):
    backend.delete_flower(flower_id)
    return redirect(url_for("frontend.index"))

@frontend_bp.route("/water/<int:flower_id>", methods=["POST"])
def water(flower_id):
    backend.water_flower(flower_id)
    return redirect(url_for("frontend.index"))