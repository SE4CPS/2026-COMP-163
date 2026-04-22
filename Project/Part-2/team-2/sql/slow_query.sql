-- Run in psql with: \i sql/slow_query.sql
-- Or paste after: \timing on

\timing on

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
-- Keep fanout in sync with backend.SLOW_QUERY_FANOUT (default 500).
CROSS JOIN generate_series(1, 500) AS s(i)
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

\timing off
