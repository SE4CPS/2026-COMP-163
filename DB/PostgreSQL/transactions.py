import psycopg2

DATABASE_URL = (
    "postgresql://neondb_owner:npg_M5sVheSzQLv4@"
    "ep-shrill-tree-a819xf7v-pooler.eastus2.azure.neon.tech/"
    "neondb?sslmode=require"
)

def run():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # create tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id SERIAL PRIMARY KEY,
        name TEXT
    );
    CREATE TABLE IF NOT EXISTS courses(
        id TEXT PRIMARY KEY,
        seats INT CHECK (seats >= 0)
    );
    CREATE TABLE IF NOT EXISTS enrollments(
        student_id INT,
        course_id TEXT
    );
    """)
    conn.commit()

    # seed
    cur.execute("INSERT INTO courses VALUES ('COMP163', 10) ON CONFLICT DO NOTHING;")
    conn.commit()

    try:
        # transaction
        cur.execute("INSERT INTO students(name) VALUES ('Tom') RETURNING id;")
        sid = cur.fetchone()[0]

        cur.execute("""
            UPDATE courses
            SET seats = seats - 1
            WHERE id='COMP163' AND seats > 0;
        """)
        if cur.rowcount == 0:
            raise Exception("No seats available")

        cur.execute(
            "INSERT INTO enrollments VALUES (%s,'COMP163');",
            (sid,)
        )

        conn.commit()
        print("SUCCESS:", sid)

    except Exception as e:
        conn.rollback()
        print("FAILED:", e)

    finally:
        cur.close()
        conn.close()

run()