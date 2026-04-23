from flask import Blueprint, request, redirect, url_for, render_template_string
import backend

frontend_bp = Blueprint("frontend", __name__)

last_flowers      = None
last_customers    = None
last_orders       = None
last_query_result = None  # dict: {query_type, elapsed, sql}
active_tab        = "flowers"

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
      --green: #4ade80;
      --red: #f87171;
      --text: #fce7f3;
      --muted: #9a7a9a;
      --card: #211221;
      --radius: 12px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'DM Mono', monospace; background-color: var(--bg); color: var(--text); min-height: 100vh; }
    body::before {
      content: '';
      position: fixed; inset: 0;
      background:
        radial-gradient(ellipse 60% 40% at 20% 10%, rgba(236,72,153,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 40% 50% at 80% 80%, rgba(244,114,182,0.05) 0%, transparent 60%);
      pointer-events: none; z-index: 0;
    }
    header {
      position: relative; z-index: 1;
      padding: 40px 60px 28px;
      border-bottom: 1px solid var(--border);
      display: flex; align-items: flex-end; gap: 24px;
    }
    header h1 { font-family: 'Playfair Display', serif; font-size: clamp(2rem,4vw,3rem); font-weight: 700; color: var(--pink-bright); }
    header p { margin-top: 6px; color: var(--muted); font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; }
    main { position: relative; z-index: 1; padding: 36px 60px; max-width: 1400px; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 24px 28px; margin-bottom: 28px; }
    .card h3 { font-family: 'Playfair Display', serif; font-size: 1.2rem; color: var(--text); margin-bottom: 18px; }
    button {
      font-family: 'DM Mono', monospace; font-size: 0.78rem; letter-spacing: 0.06em;
      padding: 9px 18px; border-radius: 8px; border: 1px solid; cursor: pointer; transition: all 0.18s ease;
    }
    .btn-primary { background: var(--pink-mid); border-color: var(--pink-mid); color: #1a0d1a; font-weight: 600; }
    .btn-primary:hover { background: var(--pink-bright); border-color: var(--pink-bright); }
    .btn-outline { background: transparent; border-color: var(--border); color: var(--muted); }
    .btn-outline:hover { border-color: var(--pink-dark); color: var(--text); }
    .btn-slow { background: rgba(248,113,113,0.15); border-color: #7f1d1d; color: var(--red); font-weight: 600; }
    .btn-slow:hover { background: rgba(248,113,113,0.3); }
    .btn-fast { background: rgba(74,222,128,0.15); border-color: #14532d; color: var(--green); font-weight: 600; }
    .btn-fast:hover { background: rgba(74,222,128,0.3); }
    .table-wrap { border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
    table { width: 100%; border-collapse: collapse; }
    thead tr { background: var(--panel); border-bottom: 1px solid var(--border); }
    th { padding: 12px 18px; text-align: left; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.12em; color: var(--muted); font-weight: 400; }
    tbody tr { border-bottom: 1px solid var(--border); transition: background 0.12s ease; }
    tbody tr:last-child { border-bottom: none; }
    tbody tr:hover { background: rgba(236,72,153,0.04); }
    td { padding: 14px 18px; font-size: 0.83rem; vertical-align: middle; }
    td.name-cell { font-family: 'Playfair Display', serif; font-size: 1rem; }
    .nav-tabs { display: flex; gap: 8px; margin-bottom: 24px; }
    .nav-tab {
      padding: 10px 20px; border-radius: 8px; border: 1px solid var(--border);
      background: transparent; color: var(--muted); font-size: 0.78rem;
      cursor: pointer; transition: all 0.18s ease; font-family: 'DM Mono', monospace;
    }
    .nav-tab.active { background: var(--pink-dark); border-color: var(--pink-dark); color: var(--text); }
    .nav-tab:hover:not(.active) { border-color: var(--pink-dark); color: var(--text); }
    .query-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
    @media (max-width: 900px) { .query-grid { grid-template-columns: 1fr; } }
    .query-box {
      background: var(--bg); border: 1px solid var(--border);
      border-radius: var(--radius); padding: 20px;
      display: flex; flex-direction: column; gap: 14px;
    }
    .query-box h4 { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; }
    .slow-label { color: var(--red); }
    .fast-label { color: var(--green); }
    .sql-block {
      background: #0d060d; border: 1px solid #2a1020; border-radius: 8px;
      padding: 14px 16px; font-size: 0.72rem; line-height: 1.7;
      white-space: pre-wrap; color: #d8b4fe; overflow-x: auto; flex: 1;
    }
    .timing-badge {
      display: inline-flex; align-items: center; gap: 8px;
      padding: 8px 16px; border-radius: 999px; font-size: 0.82rem; font-weight: 600;
    }
    .timing-slow { background: rgba(248,113,113,0.15); color: var(--red);   border: 1px solid #7f1d1d; }
    .timing-fast { background: rgba(74,222,128,0.15);  color: var(--green); border: 1px solid #14532d; }
    @media (max-width: 768px) { header, main { padding: 24px 20px; } }
  </style>
</head>
<body>

<header>
  <div>
    <h1>Flower Shop</h1>
    <p>Flowers, Customers &amp; Orders — Part 2</p>
  </div>
</header>

<main>
  <nav class="nav-tabs">
    <button class="nav-tab {% if active_tab=='flowers' %}active{% endif %}"   onclick="showTab('flowers')">Flowers</button>
    <button class="nav-tab {% if active_tab=='customers' %}active{% endif %}" onclick="showTab('customers')">Customers</button>
    <button class="nav-tab {% if active_tab=='orders' %}active{% endif %}"    onclick="showTab('orders')">Orders</button>
    <button class="nav-tab {% if active_tab=='queries' %}active{% endif %}"   onclick="showTab('queries')">Queries</button>
  </nav>

  <!-- Flowers -->
  <div id="tab-flowers" class="tab-content" {% if active_tab!='flowers' %}style="display:none;"{% endif %}>
    <div class="card">
      <h3>Our Flowers</h3>
      <form method="POST" action="{{ url_for('frontend.load_flowers') }}">
        <button type="submit" class="btn-primary">Load Flowers</button>
      </form>
    </div>
    {% if flowers %}
    <div class="table-wrap">
      <table>
        <thead><tr><th>ID</th><th>Name</th></tr></thead>
        <tbody>
          {% for r in flowers %}
          <tr><td>{{ r.id }}</td><td class="name-cell">{{ r.name }}</td></tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% endif %}
  </div>

  <!-- Customers -->
  <div id="tab-customers" class="tab-content" {% if active_tab!='customers' %}style="display:none;"{% endif %}>
    <div class="card">
      <h3>Our Customers</h3>
      <form method="POST" action="{{ url_for('frontend.load_customers') }}">
        <button type="submit" class="btn-primary">Load Customers</button>
      </form>
    </div>
    {% if customers %}
    <div class="table-wrap">
      <table>
        <thead><tr><th>ID</th><th>Name</th><th>Email</th></tr></thead>
        <tbody>
          {% for r in customers %}
          <tr><td>{{ r.id }}</td><td class="name-cell">{{ r.name }}</td><td>{{ r.email }}</td></tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% endif %}
  </div>

  <!-- Orders -->
  <div id="tab-orders" class="tab-content" {% if active_tab!='orders' %}style="display:none;"{% endif %}>
    <div class="card">
      <h3>Orders</h3>
      <form method="POST" action="{{ url_for('frontend.load_orders') }}">
        <button type="submit" class="btn-primary">Load Orders</button>
      </form>
    </div>
    {% if orders %}
    <div class="table-wrap">
      <table>
        <thead><tr><th>Order ID</th><th>Customer</th><th>Flower</th><th>Order Date</th></tr></thead>
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
    {% endif %}
  </div>

  <!-- Queries -->
  <div id="tab-queries" class="tab-content" {% if active_tab!='queries' %}style="display:none;"{% endif %}>
    <div class="query-grid">

      <!-- Slow -->
      <div class="query-box">
        <h4 class="slow-label">Slow Query</h4>
        <div class="sql-block">{{ slow_sql }}</div>
        <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
          <form method="POST" action="{{ url_for('frontend.slow_query') }}">
            <button type="submit" class="btn-slow">Run Slow Query</button>
          </form>
          {% if query_result and query_result.query_type == 'slow' %}
            <span class="timing-badge timing-slow">{{ "%.3f"|format(query_result.elapsed) }}s</span>
          {% endif %}
        </div>
      </div>

      <!-- Fast -->
      <div class="query-box">
        <h4 class="fast-label">Fast Query</h4>
        <div class="sql-block">{{ fast_sql }}</div>
        <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
          <form method="POST" action="{{ url_for('frontend.fast_query') }}">
            <button type="submit" class="btn-fast">Run Fast Query</button>
          </form>
          {% if query_result and query_result.query_type == 'fast' %}
            <span class="timing-badge timing-fast">{{ "%.3f"|format(query_result.elapsed) }}s</span>
          {% endif %}
        </div>
      </div>

    </div>
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
    global last_flowers, last_customers, last_orders, last_query_result, active_tab
    result = last_query_result
    last_query_result = None
    return render_template_string(
        PAGE,
        flowers=last_flowers,
        customers=last_customers,
        orders=last_orders,
        query_result=result,
        active_tab=active_tab,
        slow_sql=backend.SLOW_SQL,
        fast_sql=backend.FAST_SQL,
    )

@frontend_bp.route("/load/flowers", methods=["POST"])
def load_flowers():
    global last_flowers, active_tab
    last_flowers = backend.select_flower()
    active_tab = "flowers"
    return redirect(url_for("frontend.index"))

@frontend_bp.route("/load/customers", methods=["POST"])
def load_customers():
    global last_customers, active_tab
    last_customers = backend.select_customer()
    active_tab = "customers"
    return redirect(url_for("frontend.index"))

@frontend_bp.route("/load/orders", methods=["POST"])
def load_orders():
    global last_orders, active_tab
    last_orders = backend.select_order_with_details()
    active_tab = "orders"
    return redirect(url_for("frontend.index"))

@frontend_bp.route("/slow", methods=["POST"])
def slow_query():
    global last_query_result, active_tab
    elapsed, sql = backend.slow()
    last_query_result = {"query_type": "slow", "elapsed": elapsed, "sql": sql}
    active_tab = "queries"
    return redirect(url_for("frontend.index"))

@frontend_bp.route("/fast", methods=["POST"])
def fast_query():
    global last_query_result, active_tab
    elapsed, sql = backend.fast()
    last_query_result = {"query_type": "fast", "elapsed": elapsed, "sql": sql}
    active_tab = "queries"
    return redirect(url_for("frontend.index"))