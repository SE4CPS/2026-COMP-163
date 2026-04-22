from flask import Blueprint, request, redirect, url_for, render_template_string
import backend

frontend_bp = Blueprint("frontend", __name__)

PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Plant Watering Tracker</title>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=DM+Mono:wght@300;400&display=swap" rel="stylesheet"/>
  <style>
    :root {
      --bg: #0d1a0f;
      --panel: #111f14;
      --border: #1e3322;
      --green-bright: #4ade80;
      --green-mid: #22c55e;
      --green-dark: #15803d;
      --amber: #f59e0b;
      --red: #ef4444;
      --text: #d1fae5;
      --muted: #6b9a7a;
      --card: #13201a;
      --radius: 12px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'DM Mono', monospace; background-color: var(--bg); color: var(--text); min-height: 100vh; }
    body::before {
      content: '';
      position: fixed;
      inset: 0;
      background:
        radial-gradient(ellipse 60% 40% at 20% 10%, rgba(34,197,94,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 40% 50% at 80% 80%, rgba(74,222,128,0.05) 0%, transparent 60%);
      pointer-events: none;
      z-index: 0;
    }
    header {
      position: relative;
      z-index: 1;
      padding: 40px 60px 28px;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 24px;
    }
    header h1 {
      font-family: 'Playfair Display', serif;
      font-size: clamp(2rem, 4vw, 3rem);
      font-weight: 700;
      color: var(--green-bright);
      letter-spacing: -0.02em;
    }
    header p { margin-top: 6px; color: var(--muted); font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; }
    main { position: relative; z-index: 1; padding: 36px 60px; max-width: 1400px; }
    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 24px 28px;
      margin-bottom: 28px;
    }
    .card h3 {
      font-family: 'Playfair Display', serif;
      font-size: 1.2rem;
      color: var(--text);
      margin-bottom: 18px;
    }
    .row { display: flex; gap: 16px; flex-wrap: wrap; align-items: flex-end; }
    label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }
    input[type="text"], input[type="date"], input[type="number"] {
      display: block;
      margin-top: 6px;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--text);
      font-family: 'DM Mono', monospace;
      font-size: 0.85rem;
      padding: 8px 12px;
      outline: none;
      transition: border-color 0.15s;
    }
    input:focus { border-color: var(--green-dark); }
    button {
      font-family: 'DM Mono', monospace;
      font-size: 0.78rem;
      letter-spacing: 0.06em;
      padding: 9px 18px;
      border-radius: 8px;
      border: 1px solid;
      cursor: pointer;
      transition: all 0.18s ease;
    }
    .btn-primary { background: var(--green-mid); border-color: var(--green-mid); color: #0d1a0f; font-weight: 600; }
    .btn-primary:hover { background: var(--green-bright); border-color: var(--green-bright); }
    .btn-outline { background: transparent; border-color: var(--border); color: var(--muted); }
    .btn-outline:hover { border-color: var(--green-dark); color: var(--text); }
    .btn-water { background: var(--green-dark); border-color: var(--green-dark); color: var(--green-bright); padding: 6px 12px; font-size: 0.72rem; }
    .btn-water:hover { background: var(--green-mid); border-color: var(--green-mid); color: #0d1a0f; }
    .btn-edit { background: transparent; border-color: #1c3a2a; color: var(--green-mid); padding: 6px 12px; font-size: 0.72rem; }
    .btn-edit:hover { background: rgba(34,197,94,0.1); }
    .btn-danger { background: transparent; border-color: #7f1d1d; color: var(--red); padding: 6px 12px; font-size: 0.72rem; }
    .btn-danger:hover { background: rgba(239,68,68,0.1); }
    .table-wrap { border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
    table { width: 100%; border-collapse: collapse; }
    thead tr { background: var(--panel); border-bottom: 1px solid var(--border); }
    th { padding: 12px 18px; text-align: left; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.12em; color: var(--muted); font-weight: 400; }
    tbody tr { border-bottom: 1px solid var(--border); transition: background 0.12s ease; }
    tbody tr:last-child { border-bottom: none; }
    tbody tr:hover { background: rgba(34,197,94,0.04); }
    td { padding: 14px 18px; font-size: 0.83rem; vertical-align: middle; }
    td.name-cell { font-family: 'Playfair Display', serif; font-size: 1rem; color: var(--text); }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 0.7rem;
      letter-spacing: 0.06em;
      font-weight: 500;
    }
    .badge-ok { background: rgba(34,197,94,0.12); color: var(--green-mid); border: 1px solid rgba(34,197,94,0.2); }
    .badge-need { background: rgba(239,68,68,0.12); color: var(--red); border: 1px solid rgba(239,68,68,0.2); }
    .dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
    .dot-ok { background: var(--green-mid); }
    .dot-need { background: var(--red); animation: pulse 1.4s infinite; }
    @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(0.8)} }
    .actions-cell { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
    .water-inline { display: inline-flex; gap: 6px; align-items: center; }
    .water-inline input { width: 60px; margin-top: 0; padding: 6px 8px; }
    a { color: var(--green-mid); text-decoration: none; font-size: 0.72rem; }
    a:hover { color: var(--green-bright); }
    @media (max-width: 768px) { header, main { padding: 24px 20px; } }
  </style>
</head>
<body>

<header>
  <div>
    <h1>🌿 Plant Watering Tracker</h1>
    <p>Real-time watering status &amp; management</p>
  </div>
</header>

<main>
  <div class="card">
    <h3>Add Flower</h3>
    <form method="POST" action="{{ url_for('frontend.add') }}">
      <div class="row">
        <label>Name<input type="text" name="name" required></label>
        <label>Last Watered<input type="date" name="last_watered" required></label>
        <label>Water Level (inches)<input type="number" name="water_level" min="0" required></label>
        <label>Min Water Required (inches)<input type="number" name="min_water_required" min="0" required></label>
        <button type="submit" class="btn-primary">+ Add</button>
      </div>
    </form>
  </div>

  {% if edit_item %}
  <div class="card">
    <h3>Edit — {{ edit_item.name }}</h3>
    <form method="POST" action="{{ url_for('frontend.edit', id=edit_item.id) }}">
      <div class="row">
        <label>Last Watered<input type="date" name="last_watered" value="{{ edit_item.last_watered }}" required></label>
        <label>Water Level (inches)<input type="number" name="water_level" min="0" value="{{ edit_item.water_level }}" required></label>
        <button type="submit" class="btn-primary">Save</button>
        <a href="{{ url_for('frontend.index') }}" style="align-self:center;">Cancel</a>
      </div>
    </form>
  </div>
  {% endif %}

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Last Watered</th>
          <th>Water Level</th>
          <th>Min Required</th>
          <th>Current Level</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {% for r in rows %}
        <tr>
          <td>{{ r.id }}</td>
          <td class="name-cell">{{ r.name }}</td>
          <td>{{ r.last_watered }}</td>
          <td>{{ r.water_level }} in</td>
          <td>{{ r.min_water_required }} in</td>
          <td>{{ r.current_water_level }} in</td>
          <td>
            {% if r.needs_watering %}
              <span class="badge badge-need"><span class="dot dot-need"></span>Needs Water</span>
            {% else %}
              <span class="badge badge-ok"><span class="dot dot-ok"></span>OK</span>
            {% endif %}
          </td>
          <td class="actions-cell">
            <form method="POST" action="{{ url_for('frontend.water', id=r.id) }}" class="water-inline">
              <input type="number" name="amount" min="1" placeholder="in" required>
              <button type="submit" class="btn-water">💧 Water</button>
            </form>
            <a href="{{ url_for('frontend.index', edit=r.id) }}" class="btn-edit" style="padding:6px 12px; border:1px solid #1c3a2a; border-radius:8px;">Edit</a>
            <form method="POST" action="{{ url_for('frontend.delete', id=r.id) }}" style="display:inline;">
              <button type="submit" class="btn-danger" onclick="return confirm('Delete?');">Delete</button>
            </form>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</main>

</body>
</html>
"""

@frontend_bp.route("/")
def index():
    edit_id = request.args.get("edit", type=int)
    edit_item = backend.select_flower(edit_id) if edit_id else None
    rows = backend.select_flower()
    return render_template_string(PAGE, rows=rows, edit_item=edit_item)

@frontend_bp.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "").strip()
    last_watered = request.form.get("last_watered", "").strip()
    water_level = int(request.form.get("water_level", 0))
    min_water_required = int(request.form.get("min_water_required", 0))
    backend.insert_flower(name, last_watered, water_level, min_water_required)
    return redirect(url_for("frontend.index"))

@frontend_bp.route("/edit/<int:id>", methods=["POST"])
def edit(id):
    last_watered = request.form.get("last_watered", "").strip()
    water_level = int(request.form.get("water_level", 0))
    backend.update_flower(id, last_watered, water_level)
    return redirect(url_for("frontend.index"))

@frontend_bp.route("/water/<int:id>", methods=["POST"])
def water(id):
    amount = int(request.form.get("amount", 0))
    backend.water_flower(id, amount)
    return redirect(url_for("frontend.index"))

@frontend_bp.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    backend.delete_flower(id)
    return redirect(url_for("frontend.index"))
