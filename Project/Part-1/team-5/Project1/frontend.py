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
        <div style="align-self:end;"><button type="submit">Add</button></div>
      </div>
    </form>
  </div>

  {% if edit_item %}
  <div class="card">
    <h3>Edit Flower #{{ edit_item.flower_id }}</h3>
    <form method="POST" action="{{ url_for('frontend.edit', flower_id=edit_item.flower_id) }}">
      <div class="row">
        <label>Name<br><input name="name" value="{{ edit_item.name }}" required></label>
        <label>Color<br><input name="color" value="{{ edit_item.color }}" required></label>
        <label>Price<br><input name="price" type="number" step="0.01" min="0" value="{{ edit_item.price }}" required></label>
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
        <th>ID</th><th>Name</th><th>Color</th><th>Price</th><th>Actions</th>
      </tr>
    </thead>
    <tbody>
      {% for r in rows %}
      <tr>
        <td>{{ r.flower_id }}</td>
        <td>{{ r.name }}</td>
        <td>{{ r.color }}</td>
        <td>{{ r.price }}</td>
        <td>
          <a href="{{ url_for('frontend.index', edit=r.flower_id) }}">Edit</a>
          &nbsp;|&nbsp;
          <form method="POST" action="{{ url_for('frontend.delete', flower_id=r.flower_id) }}" style="display:inline;">
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
    color = (request.form.get("color", "").strip() or "Mixed")
    price = request.form.get("price", "").strip()
    backend.insert_flower(name, color, price)
    return redirect(url_for("frontend.index"))

@frontend_bp.route("/edit/<int:flower_id>", methods=["POST"])
def edit(flower_id):
    name = request.form.get("name", "").strip()
    color = request.form.get("color", "").strip()
    price = request.form.get("price", "").strip()
    backend.update_flower(flower_id, name, color, price)
    return redirect(url_for("frontend.index"))

@frontend_bp.route("/delete/<int:flower_id>", methods=["POST"])
def delete(flower_id):
    backend.delete_flower(flower_id)
    return redirect(url_for("frontend.index"))