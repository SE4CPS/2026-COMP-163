from flask import Blueprint, request, redirect, url_for, render_template_string
import backend

frontend_bp = Blueprint("frontend", __name__)

PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Flower Inventory</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; }
    th, td { border: 1px solid #ccc; padding: 8px; }
    th { background: #f3f3f3; }
    .row { display:flex; gap:12px; flex-wrap:wrap; }
    .card { border:1px solid #ddd; padding:12px; border-radius:8px; margin-bottom:16px; }
    input { padding:6px; }
    button { padding:6px 10px; cursor:pointer; }
    .needs-water { background-color: #ffcccc; }
    .is-ok { background-color: #ccffcc; }
  </style>
</head>
<body>
  <h2>Flower Inventory</h2>

  <div class="card">
    <h3>Add Flower</h3>
    <form method="POST" action="{{ url_for('frontend.add') }}">
      <div class="row">
        <label>Name<br><input name="name" required></label>
        <label>Color<br><input name="color" placeholder="Mixed"></label>
        <label>Price<br><input name="price" type="number" step="0.01" min="0" required></label>
        <label>Water Level<br><input name="water_level" type="number" value="20"></label>
        <label>Min Water Required<br><input name="min_water_required" type="number" value="5"></label>
        <div style="align-self:end;"><button type="submit">Add</button></div>
      </div>
    </form>
  </div>

  {% if edit_item %}
  <div class="card">
    <h3>Edit Flower #{{ edit_item.id }}</h3>
    <form method="POST" action="{{ url_for('frontend.edit', id=edit_item.id) }}">
      <div class="row">
        <label>Name<br><input name="name" value="{{ edit_item.name }}" required></label>
        <label>Color<br><input name="color" value="{{ edit_item.color }}" required></label>
        <label>Price<br><input name="price" type="number" step="0.01" min="0" value="{{ edit_item.price }}" required></label>
        <label>Water Level<br><input name="water_level" type="number" value="{{ edit_item.water_level }}" required></label>
        <label>Min Water Required<br><input name="min_water_required" type="number" value="{{ edit_item.min_water_required }}" required></label>
        <div style="align-self:end;">
          <button type="submit">Save</button>
          <a href="{{ url_for('frontend.index') }}" style="margin-left:10px;">Cancel</a>
        </div>
      </div>
    </form>
  </div>
  {% endif %}

  <table>
    <thead>
      <tr>
        <th>ID</th><th>Name</th><th>Color</th><th>Price</th><th>Last Watered</th><th>Water Level</th><th>Min Water Required</th><th>Actions</th>
      </tr>
    </thead>
    <tbody>
      {% for r in rows %}
      <tr class="{% if r.water_level < r.min_water_required %}needs-water{% else %}is-ok{% endif %}">
        <td>{{ r.id }}</td>
        <td>{{ r.name }}</td>
        <td>{{ r.color }}</td>
        <td>${{ "%.2f"|format(r.price) }}</td>
        <td>{{ r.last_watered }}</td>
        <td>{{ r.water_level }}</td>
        <td>{{ r.min_water_required }}</td>
        <td>
          <a href="{{ url_for('frontend.index', edit=r.id) }}">Edit</a>
          &nbsp;|&nbsp;
          <form method="POST" action="{{ url_for('frontend.water', id=r.id) }}" style="display:inline;">
            <button type="submit">Water</button>
          </form>
          &nbsp;|&nbsp;
          <form method="POST" action="{{ url_for('frontend.delete', id=r.id) }}" style="display:inline;">
            <button type="submit" onclick="return confirm('Delete this flower?');">Delete</button>
          </form>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
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
    color = request.form.get("color", "").strip() or "Mixed"
    price = float(request.form.get("price", "0"))
    water_level = int(request.form.get("water_level", "20"))
    min_water_required = int(request.form.get("min_water_required", "5"))
    
    backend.insert_flower(name, color, price, water_level, min_water_required)
    return redirect(url_for("frontend.index"))

@frontend_bp.route("/edit/<int:id>", methods=["POST"])
def edit(id):
    name = request.form.get("name", "").strip()
    color = request.form.get("color", "").strip()
    price = float(request.form.get("price", "0"))
    water_level = int(request.form.get("water_level", "0"))
    min_water_required = int(request.form.get("min_water_required", "0"))
    
    backend.update_flower(id, name, color, price, water_level, min_water_required)
    return redirect(url_for("frontend.index"))

@frontend_bp.route("/water/<int:id>", methods=["POST"])
def water(id):
    backend.water_flower(id, amount=10)
    return redirect(url_for("frontend.index"))

@frontend_bp.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    backend.delete_flower(id)
    return redirect(url_for("frontend.index"))