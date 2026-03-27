import psycopg2
import random
import time
from contextlib import contextmanager

DATABASE_URL = (
    "postgresql://neondb_owner:npg_M5sVheSzQLv4@"
    "ep-shrill-tree-a819xf7v-pooler.eastus2.azure.neon.tech/"
    "neondb?sslmode=require"
)


# =========================================================
# CONNECTION
# =========================================================

def _get_conn():
    return psycopg2.connect(DATABASE_URL)


@contextmanager
def get_conn_cursor():
    conn = _get_conn()
    cur = conn.cursor()
    try:
        yield conn, cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# =========================================================
# TIMER + SAFE EXECUTE
# =========================================================

def _is_incomplete_query(query):
    if not query:
        return True

    stripped = query.strip()

    if not stripped:
        return True

    lines = []
    for line in stripped.splitlines():
        line = line.strip()
        if line and not line.startswith("--"):
            lines.append(line)

    return len(lines) == 0


def timed_execute(cur, query, params=None, label="SQL"):
    if _is_incomplete_query(query):
        print(f"⏭ Skipping incomplete query: {label}")
        return False

    start = time.time()
    cur.execute(query, params or ())
    end = time.time()

    print(f"⏱ {label} executed in {(end - start) * 1000:.2f} ms")
    return True


# =========================================================
# TABLE PRINT
# =========================================================

def print_table(rows, headers=None):
    if not rows:
        print("No results.")
        return

    rows = [list(row) for row in rows]

    if headers is None:
        headers = [f"col{i+1}" for i in range(len(rows[0]))]

    col_widths = []
    for i in range(len(headers)):
        max_width = len(str(headers[i]))
        for row in rows:
            max_width = max(max_width, len(str(row[i])))
        col_widths.append(max_width)

    header_row = " | ".join(
        str(headers[i]).ljust(col_widths[i]) for i in range(len(headers))
    )
    separator = "-+-".join("-" * col_widths[i] for i in range(len(headers)))

    print(header_row)
    print(separator)

    for row in rows:
        print(
            " | ".join(
                str(row[i]).ljust(col_widths[i]) for i in range(len(row))
            )
        )


# =========================================================
# INIT + SEED
# =========================================================

def init_db():

    with get_conn_cursor() as (_, cur):
        timed_execute(cur, """
            CREATE TABLE IF NOT EXISTS AppUser (
                id SERIAL PRIMARY KEY,
                name VARCHAR(256) NOT NULL,
                email VARCHAR(256) NOT NULL UNIQUE
            );
        """, label="Create AppUser")

        timed_execute(cur, """
            CREATE TABLE IF NOT EXISTS Task (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title VARCHAR(256) NOT NULL,
                status VARCHAR(50) NOT NULL,
                description TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                FOREIGN KEY (user_id) REFERENCES AppUser(id) ON DELETE CASCADE,
                reminder_time TIMESTAMPTZ;
            );
        """, label="Create Task")


def seed_data():

    # Task(102, 'Alice', 'Finish presentation pending')
    # Task(200, 'Bob', 'Buy groceries is done')

    with get_conn_cursor() as (_, cur):
        timed_execute(cur, """
            -- INSERT USERS
        """, label="Insert users")

        timed_execute(cur, """
            -- INSERT TASKS
        """, label="Insert tasks")


# =========================================================
# RANDOM DATA GENERATOR
# =========================================================

def generate_random_tasks(n=10000):
    titles = [
        "Buy groceries",
        "Write report",
        "Exercise",
        "Read book",
        "Clean room",
        "Pay bills",
        "Study SQL",
        "Fix bug",
        "Email professor",
        "Prepare presentation"
    ]

    statuses = ["pending", "completed"]

    with get_conn_cursor() as (_, cur):
        for _ in range(n):
            title = random.choice(titles)
            status = random.choice(statuses)
            user_id = random.randint(1, 2)

            timed_execute(
                cur,
                """
                -- INSERT INTO Task (user_id, title, status)
                -- VALUES (%s, %s, %s)
                """,
                (user_id, title, status),
                label="Insert random task"
            )


# =========================================================
# USER OPERATIONS
# =========================================================

def create_user(username):
    with get_conn_cursor() as (_, cur):
        timed_execute(
            cur,
            """
            -- INSERT INTO AppUser (username)
            -- VALUES (%s)
            """,
            (username,),
            label="Create user"
        )


def get_all_users():
    with get_conn_cursor() as (_, cur):
        executed = timed_execute(cur, """
            -- SELECT * FROM AppUser
        """, label="Get all users")

        if not executed:
            return []

        rows = cur.fetchall()
        print_table(rows, ["user_id", "username"])
        return rows


def get_user_by_id(user_id):
    with get_conn_cursor() as (_, cur):
        executed = timed_execute(
            cur,
            """
            -- SELECT * FROM AppUser WHERE user_id = %s
            """,
            (user_id,),
            label="Get user by id"
        )

        if not executed:
            return None

        row = cur.fetchone()

        if row:
            print_table([row], ["user_id", "username"])
        else:
            print("No results.")

        return row


# =========================================================
# TASK OPERATIONS
# =========================================================

def create_task(user_id, title, status="pending"):
    with get_conn_cursor() as (_, cur):
        timed_execute(
            cur,
            """
            -- INSERT INTO Task (user_id, title, status)
            -- VALUES (%s, %s, %s)
            """,
            (user_id, title, status),
            label="Create task"
        )


def get_all_tasks():
    with get_conn_cursor() as (_, cur):
        executed = timed_execute(cur, """
            -- SELECT * FROM Task
        """, label="Get all tasks")

        if not executed:
            return []

        rows = cur.fetchall()
        print_table(rows, ["task_id", "user_id", "title", "status"])
        return rows


def get_tasks_by_user(user_id):
    with get_conn_cursor() as (_, cur):
        executed = timed_execute(
            cur,
            """
            -- SELECT * FROM Task WHERE user_id = %s
            """,
            (user_id,),
            label="Get tasks by user"
        )

        if not executed:
            return []

        rows = cur.fetchall()
        print_table(rows, ["task_id", "user_id", "title", "status"])
        return rows


def get_completed_tasks():
    with get_conn_cursor() as (_, cur):
        executed = timed_execute(cur, """
            -- SELECT * FROM Task WHERE status = 'completed'
        """, label="Get completed tasks")

        if not executed:
            return []

        rows = cur.fetchall()
        print_table(rows, ["task_id", "user_id", "title", "status"])
        return rows


def update_task_status(task_id, status):
    with get_conn_cursor() as (_, cur):
        timed_execute(
            cur,
            """
            -- UPDATE Task SET status = %s WHERE task_id = %s
            """,
            (status, task_id),
            label="Update task status"
        )


def delete_task(task_id):
    with get_conn_cursor() as (_, cur):
        timed_execute(
            cur,
            """
            -- DELETE FROM Task WHERE task_id = %s
            """,
            (task_id,),
            label="Delete task"
        )


# =========================================================
# TRANSACTION EXAMPLES
# =========================================================

def create_user_with_tasks(username, tasks):
    with get_conn_cursor() as (_, cur):
        timed_execute(cur, """
            -- INSERT USER
        """, label="Insert user in transaction")

        for task in tasks:
            timed_execute(cur, """
                -- INSERT TASK FOR USER
            """, label="Insert task in transaction")


def transfer_task(task_id, new_user_id):
    with get_conn_cursor() as (_, cur):
        timed_execute(cur, """
            -- VALIDATE TASK EXISTS
        """, label="Validate task exists")

        timed_execute(
            cur,
            """
            -- UPDATE Task SET user_id = %s WHERE task_id = %s
            """,
            (new_user_id, task_id),
            label="Transfer task"
        )


def replace_tasks(user_id, new_tasks):
    with get_conn_cursor() as (_, cur):
        timed_execute(
            cur,
            """
            -- DELETE FROM Task WHERE user_id = %s
            """,
            (user_id,),
            label="Delete old tasks"
        )

        for task in new_tasks:
            timed_execute(cur, """
                -- INSERT NEW TASK
            """, label="Insert replacement task")


# =========================================================
# INDEXING
# =========================================================

def create_status_index():
    with get_conn_cursor() as (_, cur):
        timed_execute(cur, """
            -- CREATE INDEX idx_task_status ON Task(status)
        """, label="Create status index")

# =========================================================
# ENCRYPT / DECRYPT
# =========================================================

def encrypt_user_email(user_id):

    with get_conn_cursor() as (_, cur):
        timed_execute(cur, """
            -- CREATE EXTENSION IF NOT EXISTS pgcrypto
        """, label="Enable pgcrypto")

        timed_execute(cur, """
            -- UPDATE AppUser
            -- SET email = email
            -- WHERE id = %s
        """, (user_id,), label="Encrypt user email")

def decrypt_user_email(user_id):

    with get_conn_cursor() as (_, cur):
        timed_execute(cur, """
            -- SELECT email
            -- FROM AppUser
            -- WHERE id = %s
        """, (user_id,), label="Decrypt user email")

# =========================================================
# CURRENT USER
# =========================================================

def get_current_user():

    with get_conn_cursor() as (_, cur):
        timed_execute(cur, """
            SELECT current_user
        """, label="Get current user")

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    init_db()
    seed_data()

    # generate_random_tasks(10000)
    # create_status_index()
    # get_all_users()
    # get_user_by_id(1)
    # get_all_tasks()
    # get_tasks_by_user(1)
    # get_completed_tasks()

    print("App ready for implementation...")
