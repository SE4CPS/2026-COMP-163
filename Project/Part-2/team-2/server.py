"""
Team 2 — Part 2: slow query demo + timing endpoint.
"""

import os
import time

from flask import Flask, jsonify, render_template

import admin
import backend

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(_BASE_DIR, "templates"))

_HOME_HTML = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Team 2 Part 2</title></head>
<body style="font-family:system-ui;margin:2rem;line-height:1.5">
  <h1>Team 2 — Part 2</h1>
  <p>Your server is running. Use these routes:</p>
  <ul>
    <li><a href="/part2/benchmark"><strong>Part 2 benchmark (Slow / Fast buttons)</strong></a></li>
    <li><a href="/health"><code>GET /health</code></a> — quick JSON check</li>
    <li><a href="/part2/slow-query"><code>GET /part2/slow-query</code></a> — slow query JSON (can take a long time)</li>
  </ul>
  <p>To re-run <code>init_db</code> + <code>seed_data</code>: <code>curl -X POST http://127.0.0.1:5002/part2/init</code></p>
</body>
</html>"""


@app.route("/", methods=["GET"])
def index():
    return _HOME_HTML, 200, {"Content-Type": "text/html; charset=utf-8"}


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "team": 2, "part": 2})


@app.route("/part2/init", methods=["POST"])
def part2_init():
    """Recreate Part 2 tables and seed (dev / grading)."""
    admin.init_db()
    admin.seed_data()
    return jsonify({"message": "init_db + seed_data completed."})


@app.route("/part2/benchmark", methods=["GET"])
def part2_benchmark():
    """HTML UI: SQL text + Slow / Fast buttons; timings only (no result rows)."""
    return render_template(
        "part2.html",
        slow_sql=backend.SLOW_QUERY_SQL.strip(),
        fast_sql=backend.FAST_QUERY_SQL.strip(),
    )


@app.post("/part2/api/slow-query")
def api_slow_query():
    """Run slow query; JSON includes SQL text and timings only (no row payload)."""
    try:
        wall0 = time.perf_counter()
        elapsed_db, row_count = backend.run_slow_query()
        wall = time.perf_counter() - wall0
        return jsonify(
            {
                "query": backend.SLOW_QUERY_SQL.strip(),
                "wall_clock_seconds": round(wall, 3),
                "db_execute_fetch_seconds": round(elapsed_db, 3),
                "row_count": row_count,
            }
        )
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.post("/part2/api/fast-query")
def api_fast_query():
    """Run optimized query; JSON includes SQL text and timings only (no row payload)."""
    try:
        wall0 = time.perf_counter()
        elapsed_db, row_count = backend.run_fast_query()
        wall = time.perf_counter() - wall0
        return jsonify(
            {
                "query": backend.FAST_QUERY_SQL.strip(),
                "wall_clock_seconds": round(wall, 3),
                "db_execute_fetch_seconds": round(elapsed_db, 3),
                "row_count": row_count,
            }
        )
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/part2/slow-query", methods=["GET"])
def part2_slow_query():
    """
    End-to-end timing: HTTP handler through DB execute + fetchall.
    Expect >15s total when the database query exceeds ~10s.
    """
    wall0 = time.perf_counter()
    elapsed_db, row_count = backend.run_slow_query()
    wall1 = time.perf_counter()
    wall = wall1 - wall0
    return jsonify(
        {
            "team": 2,
            "wall_clock_seconds": round(wall, 3),
            "db_execute_fetch_seconds": round(elapsed_db, 3),
            "row_count": row_count,
            "fanout": backend.SLOW_QUERY_FANOUT,
            "note": (
                "Increase backend.SLOW_QUERY_FANOUT if DB time is under 10s on your hardware."
            ),
        }
    )


if __name__ == "__main__":
    admin.init_db()
    admin.seed_data()
    app.run(host="127.0.0.1", port=5002, debug=False)
