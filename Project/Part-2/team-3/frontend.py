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
    :root {
      --primary: #2e7d32;
      --primary-hover: #1b5e20;
      --danger: #d32f2f;
      --danger-hover: #c62828;
      --bg: #f5f7fa;
      --card-bg: #ffffff;
      --text: #333333;
    }
    body { 
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; 
      margin: 0; padding: 32px; 
      background-color: var(--bg); color: var(--text);
    }
    h2, h3 { color: #1a1a1a; margin-top: 0; }
    .card { 
      background: var(--card-bg); border: none; padding: 24px; 
      border-radius: 12px; margin-bottom: 24px; 
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
    }
    .row { display: flex; gap: 16px; flex-wrap: wrap; align-items: flex-end; }
    label { font-size: 0.9em; font-weight: 500; color: #555; display: block; margin-bottom: 6px; }
    input { 
      padding: 10px 12px; border: 1px solid #ddd; border-radius: 6px; 
      font-size: 14px; transition: border-color 0.2s; 
    }
    input:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(46,125,50,0.1); }
    button { 
      padding: 10px 16px; cursor: pointer; background-color: var(--primary); 
      color: white; border: none; border-radius: 6px; font-weight: 600; 
      font-size: 14px; transition: background-color 0.2s;
    }
    button:hover { background-color: var(--primary-hover); }
    .btn-danger { background-color: var(--danger); }
    .btn-danger:hover { background-color: var(--danger-hover); }
    table { 
      border-collapse: separate; border-spacing: 0; width: 100%; 
      background: var(--card-bg); border-radius: 12px; overflow: hidden;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-top: 12px;
    }
    th, td { padding: 14px 16px; text-align: left; border-bottom: 1px solid #edf2f7; }
    th { background: #f8fafc; font-weight: 600; color: #4a5568; text-transform: uppercase; font-size: 0.85em; letter-spacing: 0.05em; }
    .needs-water { background-color: #fff5f5; }
    .is-ok { background-color: #f0fff4; }
    a { color: var(--primary); text-decoration: none; font-weight: 500; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <h2>Flower Inventory</h2>

  <div class="card">
    <h3>Performance Testing (Part 2)</h3>
    <div class="row">
      <div style="flex:1; border: 1px solid #ddd; padding: 12px; border-radius: 8px;">
        <button type="button" onclick="runQuery('/slow_query', 'slow')">Run Slow Query</button>
        <p><strong>Execution Time:</strong> <span id="slow-time">N/A</span></p>
        <pre id="slow-sql" style="background:#f3f3f3; padding:8px; font-size:12px; white-space: pre-wrap; word-wrap: break-word;">/* SQL will appear here */</pre>
      </div>
      <div style="flex:1; border: 1px solid #ddd; padding: 12px; border-radius: 8px;">
        <button type="button" onclick="runQuery('/fast_query', 'fast')">Run Fast Query</button>
        <p><strong>Execution Time:</strong> <span id="fast-time">N/A</span></p>
        <pre id="fast-sql" style="background:#f3f3f3; padding:8px; font-size:12px; white-space: pre-wrap; word-wrap: break-word;">/* SQL will appear here */</pre>
      </div>
    </div>
  </div>

  <div class="card">
    <h3>Add Flower</h3>
    <form method="POST" action="{{ url_for('frontend.add') }}">
      <div class="row">
        <div><label>Name</label><input name="name" required></div>
        <div><label>Color</label><input name="color" placeholder="Mixed"></div>
        <div><label>Price</label><input name="price" type="number" step="0.01" min="0" required></div>
        <div><label>Water Level</label><input name="water_level" type="number" value="20"></div>
        <div><label>Min Water Required</label><input name="min_water_required" type="number" value="5"></div>
        <div style="align-self:end;"><button type="submit">Add</button></div>
      </div>
    </form>
  </div>

  {% if edit_item %}
  <div class="card">
    <h3>Edit Flower #{{ edit_item.id }}</h3>
    <form method="POST" action="{{ url_for('frontend.edit', id=edit_item.id) }}">
      <div class="row">
        <div><label>Name</label><input name="name" value="{{ edit_item.name }}" required></div>
        <div><label>Color</label><input name="color" value="{{ edit_item.color }}" required></div>
        <div><label>Price</label><input name="price" type="number" step="0.01" min="0" value="{{ edit_item.price }}" required></div>
        <div><label>Water Level</label><input name="water_level" type="number" value="{{ edit_item.water_level }}" required></div>
        <div><label>Min Water Required</label><input name="min_water_required" type="number" value="{{ edit_item.min_water_required }}" required></div>
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
            <button type="submit" class="btn-danger" onclick="return confirm('Delete this flower?');">Delete</button>
          </form>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <script>
    function runQuery(endpoint, type) {
      document.getElementById(type + '-time').innerText = "Running...";
      document.getElementById(type + '-sql').innerText = "Executing query...";
      
      fetch(endpoint)
        .then(response => response.json())
        .then(data => {
          document.getElementById(type + '-time').innerText = data.execution_time_seconds + " seconds";
          document.getElementById(type + '-sql').innerText = data.query;
        })
        .catch(error => {
          document.getElementById(type + '-time').innerText = "Error executing query";
          console.error(error);
        });
    }
  </script>
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