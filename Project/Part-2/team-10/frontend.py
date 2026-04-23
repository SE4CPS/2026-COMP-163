from flask import Blueprint, request, redirect, url_for, render_template_string
import backend

frontend_bp = Blueprint("frontend", __name__)

last_query_result = None

PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Flower Shop</title>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=DM+Mono:wght@300;400&display=swap" rel="stylesheet"/>
  <style>
    :root {
      --bg: #1a0d1a;
      --panel: #1f111f;
      --border: #331e33;
      --pink-bright: #f472b6;
      --pink-mid: #ec4899;
      --pink-dark: #be185d;
      --rose: #9f1239;
      --amber: #f59e0b;
      --text: #fce7f3;
      --muted: #9a7a9a;
      --card: #211221;
      --radius: 12px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'DM Mono', monospace; background-color: var(--bg); color: var(--text); min-height: 100vh; }
    body::before {
      content: '';
      position: fixed;
      inset: 0;
      background:
        radial-gradient(ellipse 60% 40% at 20% 10%, rgba(236,72,153,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 40% 50% at 80% 80%, rgba(244,114,182,0.05) 0%, transparent 60%);
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
      color: var(--pink-bright);
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
    input[type="text"], input[type="date"], input[type="number"], select {
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
    input:focus, select:focus { border-color: var(--pink-dark); }
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
    .btn-primary { background: var(--pink-mid); border-color: var(--pink-mid); color: #1a0d1a; font-weight: 600; }
    .btn-primary:hover { background: var(--pink-bright); border-color: var(--pink-bright); }
    .btn-outline { background: transparent; border-color: var(--border); color: var(--muted); }
    .btn-outline:hover { border-color: var(--pink-dark); color: var(--text); }
    .table-wrap { border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
    table { width: 100%; border-collapse: collapse; }
    thead tr { background: var(--panel); border-bottom: 1px solid var(--border); }
    th { padding: 12px 18px; text-align: left; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.12em; color: var(--muted); font-weight: 400; }
    tbody tr { border-bottom: 1px solid var(--border); transition: background 0.12s ease; }
    tbody tr:last-child { border-bottom: none; }
    tbody tr:hover { background: rgba(236,72,153,0.04); }
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
    .badge-pink { background: rgba(236,72,153,0.12); color: var(--pink-mid); border: 1px solid rgba(236,72,153,0.2); }
    .nav-tabs { display: flex; gap: 8px; margin-bottom: 24px; }
    .nav-tab {
      padding: 10px 20px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: transparent;
      color: var(--muted);
      font-size: 0.78rem;
      cursor: pointer;
      transition: all 0.18s ease;
    }
    .nav-tab.active { background: var(--pink-dark); border-color: var(--pink-dark); color: var(--text); }
    .nav-tab:hover:not(.active) { border-color: var(--pink-dark); color: var(--text); }
    a { color: var(--pink-mid); text-decoration: none; font-size: 0.72rem; }
    a:hover { color: var(--pink-bright); }
    @media (max-width: 768px) { header, main { padding: 24px 20px; } }
    pre { background: var(--bg); padding: 16px; border-radius: 8px; overflow-x: auto; font-size: 0.75rem; white-space: pre-wrap; }
  </style>
</head>
<body>

<header>
  <div>
    <h1>Flower Shop</h1>
    <p>Flowers, Customers &amp; Orders</p>
  </div>
</header>

<main>
  <nav class="nav-tabs">
    <button class="nav-tab active" onclick="showTab('flowers')">Flowers</button>
    <button class="nav-tab" onclick="showTab('customers')">Customers</button>
    <button class="nav-tab" onclick="showTab('orders')">Orders</button>
    <button class="nav-tab" onclick="showTab('queries')">Queries</button>
  </nav>

  <div id="tab-flowers" class="tab-content">
    <div class="card">
      <h3>Our Flowers</h3>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
          </tr>
        </thead>
        <tbody>
          {% for r in flowers %}
          <tr>
            <td>{{ r.id }}</td>
            <td class="name-cell">{{ r.name }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>

  <div id="tab-customers" class="tab-content" style="display:none;">
    <div class="card">
      <h3>Our Customers</h3>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
          </tr>
        </thead>
        <tbody>
          {% for r in customers %}
          <tr>
            <td>{{ r.id }}</td>
            <td class="name-cell">{{ r.name }}</td>
            <td>{{ r.email }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>

  <div id="tab-orders" class="tab-content" style="display:none;">
    <div class="card">
      <h3>Orders</h3>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Customer</th>
            <th>Flower</th>
            <th>Order Date</th>
          </tr>
        </thead>
        <tbody>
          {% for r in orders %}
          <tr>
            <td>{{ r.order_id }}</td>
            <td>{{ r.customer_name }}</td>
            <td>{{ r.flower_name }}</td>
            <td>{{ r.order_date }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>

  <div id="tab-queries" class="tab-content" style="display:none;">
    <div class="card">
      <h3>Database Queries</h3>
      <div class="row">
        <form method="POST" action="{{ url_for('frontend.slow_query') }}">
          <button type="submit" class="btn-outline">Time Slow Query</button>
        </form>
        <form method="POST" action="{{ url_for('frontend.fast_query') }}">
          <button type="submit" class="btn-primary">Time Fast Query</button>
        </form>
      </div>
    </div>
    {% if query_result %}
    <div class="card">
      <h3>Query Time: {{ query_result }}</h3>
    </div>
    {% endif %}
  </div>
</main>

<script>
  function showTab(tab) {
    document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.nav-tab').forEach(el => el.classList.remove('active'));
    document.getElementById('tab-' + tab).style.display = 'block';
    event.target.classList.add('active');
  }
</script>

</body>
</html>
"""

@frontend_bp.route("/")
def index():
    global last_query_result
    flowers = backend.select_flower()
    customers = backend.select_customer()
    orders = backend.select_order_with_details()
    result = last_query_result
    last_query_result = None
    return render_template_string(PAGE, flowers=flowers, customers=customers, orders=orders, query_result=result)

@frontend_bp.route("/slow", methods=["POST"])
def slow_query():
    global last_query_result
    last_query_result = backend.slow()
    return redirect(url_for("frontend.index"))

@frontend_bp.route("/fast", methods=["POST"])
def fast_query():
    global last_query_result
    last_query_result = backend.fast()
    return redirect(url_for("frontend.index"))