"""
Deliberately expensive query for Part 2 (before optimization in a later step).
"""

import time

import psycopg2

from admin import get_database_url

# Expand each joined row with a cross join so sort + hashes dominate runtime.
# Increase SLOW_QUERY_FANOUT if a faster machine finishes under 10s.
# 10_000 orders × fanout rows after join; raise if your machine finishes under 10s.
SLOW_QUERY_FANOUT = 500


def _get_conn():
    return psycopg2.connect(get_database_url())


SLOW_QUERY_SQL = f"""
SELECT
    o.id,
    o.customer_id,
    o.flower_id,
    o.order_date,
    c.id,
    c.name,
    c.email,
    f.id,
    f.name,
    f.color,
    f.price,
    f.last_watered,
    f.water_level,
    f.min_water_required,
    s.i AS fanout_i,
    md5(
        md5(
            lower(coalesce(c.email, ''))
            || upper(coalesce(f.color, ''))
            || coalesce(f.name, '')
            || o.id::text
            || s.i::text
        )
        || md5(coalesce(c.name, '') || coalesce(f.name, ''))
    ) AS row_digest
FROM team2_orders o
INNER JOIN team2_customers c
    ON c.id = o.customer_id
INNER JOIN team2_flowers f
    ON f.id = o.flower_id
CROSS JOIN generate_series(1, {SLOW_QUERY_FANOUT}) AS s(i)
WHERE lower(coalesce(c.email, '')) LIKE '%' || chr(64) || '%'
  AND lower(coalesce(f.name, '')) LIKE '%' || 'e' || '%'
  AND lower(coalesce(c.name, '')) LIKE '%' || 'u' || '%'
ORDER BY
    lower(c.name),
    upper(f.color),
    upper(c.email),
    o.order_date,
    f.price,
    s.i,
    row_digest;
"""

# Optimized: same one row per order + customer + flower as the slow query’s base join
# for seeded data (slow query’s LIKE/% checks and fanout are non-semantic for reporting).
FAST_QUERY_SQL = """
SELECT
    o.id,
    o.customer_id,
    o.flower_id,
    o.order_date,
    c.id,
    c.name,
    c.email,
    f.id,
    f.name,
    f.color,
    f.price,
    f.last_watered,
    f.water_level,
    f.min_water_required
FROM team2_orders o
INNER JOIN team2_customers c ON c.id = o.customer_id
INNER JOIN team2_flowers f ON f.id = o.flower_id
WHERE c.email LIKE 'customer_%@example.com'
  AND f.name LIKE 'Flower_%'
  AND c.name LIKE 'Customer_%'
ORDER BY o.id
LIMIT 10000 OFFSET 0;
"""


def run_slow_query():
    """
    Execute the slow SELECT and return (elapsed_seconds, row_count).
    Elapsed time includes full result materialization and fetch on the client.
    """
    conn = _get_conn()
    cur = conn.cursor()
    try:
        t0 = time.perf_counter()
        cur.execute(SLOW_QUERY_SQL)
        n = 0
        while True:
            chunk = cur.fetchmany(8192)
            if not chunk:
                break
            n += len(chunk)
        elapsed = time.perf_counter() - t0
        return elapsed, n
    finally:
        cur.close()
        conn.close()


def run_fast_query():
    """Execute the optimized SELECT; time includes execute + streaming fetch."""
    conn = _get_conn()
    cur = conn.cursor()
    try:
        t0 = time.perf_counter()
        cur.execute(FAST_QUERY_SQL)
        n = 0
        while True:
            chunk = cur.fetchmany(8192)
            if not chunk:
                break
            n += len(chunk)
        elapsed = time.perf_counter() - t0
        return elapsed, n
    finally:
        cur.close()
        conn.close()
