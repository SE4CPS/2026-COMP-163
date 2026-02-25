from flask import Blueprint, request, redirect, render_template_string
import backend

frontend_bp = Blueprint("frontend", __name__)

PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Hiking Reservation System</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 18px; }
    h2, h3 { margin: 10px 0; }
    .split { display: flex; gap: 18px; align-items: flex-start; }
    .card { border: 1px solid #ddd; padding: 12px; border-radius: 8px; width: 48%; }
    label { display: block; margin-top: 8px; }
    input, select { width: 100%; padding: 6px; margin-top: 4px; }
    button { margin-top: 10px; padding: 8px 10px; cursor: pointer; }
    table { border-collapse: collapse; width: 100%; margin-top: 10px; }
    th, td { border: 1px solid #ddd; padding: 6px; text-align: left; vertical-align: top; }
    th { background: #f7f7f7; }
    .small { font-size: 0.9em; color: #666; }
    .row { display: flex; gap: 10px; }
    .row > div { flex: 1; }
    .danger { color: #b00020; }
  </style>
</head>
<body>

  <h2>Hiking Reservation System</h2>
  <div class="small">
    Two tables: <b>trail</b> and <b>reservation</b>. Practice JOIN, GROUP BY, HAVING, LIMIT, OFFSET.
  </div>

  <div class="split" style="margin-top: 14px;">
    <div class="card">
      <h3>Add Trail</h3>
      <form method="post" action="/trail/create">
        <label>Trail name</label>
        <input name="name" placeholder="e.g., River Loop" required />

        <div class="row">
          <div>
            <label>Difficulty</label>
            <select name="difficulty">
              <option value="Easy">Easy</option>
              <option value="Moderate">Moderate</option>
              <option value="Hard">Hard</option>
            </select>
          </div>
          <div>
            <label>Capacity</label>
            <input name="capacity" type="number" min="1" value="10" required />
          </div>
        </div>

        <button type="submit">Create Trail</button>
      </form>

      <hr />

      <h3>Add Reservation</h3>
      <form method="post" action="/reservation/create">
        <label>Hiker name</label>
        <input name="hiker_name" placeholder="e.g., Alex" required />

        <label>Hike date</label>
        <input name="hike_date" type="date" required />

        <label>Trail</label>
        <select name="trail_id" required>
          {% for t in trails %}
            <option value="{{ t.trail_id }}">{{ t.trail_id }} - {{ t.name }} ({{ t.difficulty }})</option>
          {% endfor %}
        </select>

        <button type="submit">Create Reservation</button>
      </form>
    </div>

    <div class="card">
      <h3>Trails</h3>
      {% if trail_cols %}
      <table>
        <thead>
          <tr>
            {% for col in trail_cols %}
              <th>{{ col }}</th>
            {% endfor %}
            <th>actions</th>
          </tr>
        </thead>
        <tbody>
          {% for row in trails %}
          <tr>
            {% for col in trail_cols %}
              <td>{{ row.get(col, "") }}</td>
            {% endfor %}
            <td>
              <form method="post" action="/trail/delete" style="margin:0;">
                <input type="hidden" name="trail_id" value="{{ row.get('trail_id') }}">
                <button type="submit">delete</button>
              </form>
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
      {% else %}
        <div class="small">No trails yet.</div>
      {% endif %}
    </div>
  </div>

  <div class="card" style="width: 100%; margin-top: 18px;">
    <h3>Reservations Joined with Trails</h3>
    <div class="small">
      This table adapts to whatever columns your JOIN query returns.
      Students can change SELECT columns and the table updates.
    </div>

    {% if reservation_cols %}
    <table>
      <thead>
        <tr>
          {% for col in reservation_cols %}
            <th>{{ col }}</th>
          {% endfor %}
          <th>actions</th>
        </tr>
      </thead>
      <tbody>
        {% for row in reservations %}
        <tr>
          {% for col in reservation_cols %}
            <td>{{ row.get(col, "") }}</td>
          {% endfor %}
          <td>
            <form method="post" action="/reservation/delete" style="margin:0;">
              <input type="hidden" name="reservation_id" value="{{ row.get('reservation_id') }}">
              <button type="submit">delete</button>
            </form>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    {% else %}
      <div class="small">No reservations yet.</div>
    {% endif %}
  </div>

</body>
</html>
"""


@frontend_bp.route("/")
def index():
    trails = backend.select_trails()
    reservations = backend.select_reservations_join()

    # Dynamic columns based on dict keys (safe as long as backend returns dict rows)
    trail_cols = list(trails[0].keys()) if trails else []
    reservation_cols = list(reservations[0].keys()) if reservations else []

    return render_template_string(
        PAGE,
        trails=trails,
        reservations=reservations,
        trail_cols=trail_cols,
        reservation_cols=reservation_cols,
    )


@frontend_bp.route("/trail/create", methods=["POST"])
def trail_create():
    name = (request.form.get("name") or "").strip()
    difficulty = (request.form.get("difficulty") or "Easy").strip()
    capacity = request.form.get("capacity") or "10"
    backend.insert_trail(name, difficulty, capacity)
    return redirect("/")


@frontend_bp.route("/trail/delete", methods=["POST"])
def trail_delete():
    trail_id = request.form.get("trail_id")
    if trail_id:
        backend.delete_trail(trail_id)
    return redirect("/")


@frontend_bp.route("/reservation/create", methods=["POST"])
def reservation_create():
    hiker_name = (request.form.get("hiker_name") or "").strip()
    hike_date = (request.form.get("hike_date") or "").strip()
    trail_id = request.form.get("trail_id") or ""
    backend.insert_reservation(hiker_name, hike_date, trail_id)
    return redirect("/")


@frontend_bp.route("/reservation/delete", methods=["POST"])
def reservation_delete():
    reservation_id = request.form.get("reservation_id")
    if reservation_id:
        backend.delete_reservation(reservation_id)
    return redirect("/")