from flask import Blueprint, request, redirect, url_for, render_template_string
import backend

frontend_bp = Blueprint("frontend", __name__)

PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Hiking Reservation System</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; }
    th, td { border: 1px solid #ccc; padding: 8px; }
    th { background: #f3f3f3; }
    .row { display:flex; gap:12px; flex-wrap:wrap; align-items:end; }
    .card { border:1px solid #ddd; padding:12px; border-radius:8px; margin-bottom:16px; }
    input, select { padding:6px; }
    button { padding:6px 10px; cursor:pointer; }
    h2 { margin-top: 0; }
  </style>
</head>
<body>
  <h2>Hiking Reservation System</h2>

  <div class="card">
    <h3>Add Trail</h3>
    <form method="POST" action="{{ url_for('frontend.add_trail') }}">
      <div class="row">
        <label>Trail Name<br><input name="name" required></label>
        <label>Difficulty<br><input name="difficulty" placeholder="Easy"></label>
        <label>Capacity<br><input name="capacity" type="number" min="0" value="10" required></label>
        <button type="submit">Add Trail</button>
      </div>
    </form>
  </div>

  <div class="card">
    <h3>Add Reservation</h3>
    <form method="POST" action="{{ url_for('frontend.add_reservation') }}">
      <div class="row">
        <label>Hiker Name<br><input name="hiker_name" required></label>
        <label>Date (YYYY-MM-DD)<br><input name="hike_date" placeholder="2026-02-15" required></label>
        <label>Trail<br>
          <select name="trail_id" required>
            {% for t in trails %}
              <option value="{{ t.trail_id }}">{{ t.trail_id }} — {{ t.name }}</option>
            {% endfor %}
          </select>
        </label>
        <button type="submit">Reserve</button>
      </div>
    </form>
  </div>

  <h3>Trails</h3>
  <table>
    <thead>
      <tr>
        <th>ID</th><th>Name</th><th>Difficulty</th><th>Capacity</th><th>Actions</th>
      </tr>
    </thead>
    <tbody>
      {% for t in trails %}
      <tr>
        <td>{{ t.trail_id }}</td>
        <td>{{ t.name }}</td>
        <td>{{ t.difficulty }}</td>
        <td>{{ t.capacity }}</td>
        <td>
          <form method="POST" action="{{ url_for('frontend.delete_trail', trail_id=t.trail_id) }}" style="display:inline;">
            <button type="submit" onclick="return confirm('Delete this trail?');">Delete</button>
          </form>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <h3>Reservations (JOIN: Reservation ⨝ Trail)</h3>
  <table>
    <thead>
      <tr>
        <th>Res ID</th><th>Hiker</th><th>Date</th><th>Trail</th><th>Difficulty</th><th>Actions</th>
      </tr>
    </thead>
    <tbody>
      {% for r in reservations %}
      <tr>
        <td>{{ r.reservation_id }}</td>
        <td>{{ r.hiker_name }}</td>
        <td>{{ r.hike_date }}</td>
        <td>{{ r.trail_name }} (ID {{ r.trail_id }})</td>
        <td>{{ r.difficulty }}</td>
        <td>
          <form method="POST" action="{{ url_for('frontend.delete_reservation', reservation_id=r.reservation_id) }}" style="display:inline;">
            <button type="submit" onclick="return confirm('Delete this reservation?');">Delete</button>
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
    trails = backend.select_trails()
    reservations = backend.select_reservations_join()
    return render_template_string(PAGE, trails=trails, reservations=reservations)


@frontend_bp.route("/trail/add", methods=["POST"])
def add_trail():
    name = request.form.get("name", "").strip()
    difficulty = (request.form.get("difficulty", "").strip() or "Easy")
    capacity = request.form.get("capacity", "10").strip()
    backend.insert_trail(name, difficulty, capacity)
    return redirect(url_for("frontend.index"))


@frontend_bp.route("/trail/delete/<int:trail_id>", methods=["POST"])
def delete_trail(trail_id):
    backend.delete_trail(trail_id)
    return redirect(url_for("frontend.index"))


@frontend_bp.route("/reservation/add", methods=["POST"])
def add_reservation():
    hiker_name = request.form.get("hiker_name", "").strip()
    hike_date = request.form.get("hike_date", "").strip()
    trail_id = request.form.get("trail_id", "").strip()
    backend.insert_reservation(hiker_name, hike_date, trail_id)
    return redirect(url_for("frontend.index"))


@frontend_bp.route("/reservation/delete/<int:reservation_id>", methods=["POST"])
def delete_reservation(reservation_id):
    backend.delete_reservation(reservation_id)
    return redirect(url_for("frontend.index"))
