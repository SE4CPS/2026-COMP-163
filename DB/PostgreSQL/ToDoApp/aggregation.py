import os
import random
import time
from contextlib import contextmanager

import psycopg2
from dotenv import load_dotenv

load_dotenv()

# =========================================================
# ENV
# =========================================================

POSTGRES_DATABASE_URL = os.getenv("DATABASE_URL")


# =========================================================
# POSTGRES CONNECTION
# =========================================================

def _get_postgres_conn():
    return psycopg2.connect(POSTGRES_DATABASE_URL)


@contextmanager
def get_postgres_conn_cursor():
    conn = _get_postgres_conn()
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
# TIMER
# =========================================================

def timed_postgres_execute(cur, query, params=None, label="Postgres SQL"):
    start = time.time()
    cur.execute(query, params or ())
    end = time.time()
    elapsed_ms = (end - start) * 1000
    print(f"⏱ {label} executed in {elapsed_ms:.2f} ms")
    return elapsed_ms


def print_rows(rows):
    if not rows:
        print("No results.")
        return

    for row in rows:
        print(row)


# =========================================================
# TABLE SETUP
# =========================================================

def create_task_table():
    with get_postgres_conn_cursor() as (_, cur):
        timed_postgres_execute(
            cur,
            """
            DROP TABLE IF EXISTS task;

            CREATE TABLE IF NOT EXISTS task (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                status VARCHAR(50) NOT NULL,
                priority INTEGER NOT NULL,
                estimated_hours INTEGER NOT NULL
            );
            """,
            label="Create task table"
        )


def drop_task_table():
    with get_postgres_conn_cursor() as (_, cur):
        timed_postgres_execute(
            cur,
            """
            DROP TABLE IF EXISTS task;
            """,
            label="Drop task table"
        )


# =========================================================
# DATA GENERATION
# =========================================================

def build_random_task_rows(n=10000):
    titles = [
        "Write report",
        "Fix login bug",
        "Study SQL",
        "Prepare slides",
        "Submit assignment",
        "Read chapter",
        "Update website",
        "Test API",
        "Clean dataset",
        "Review code"
    ]

    statuses = ["pending", "in_progress", "completed"]

    rows = []
    for _ in range(n):
        rows.append(
            (
                random.choice(titles),
                random.choice(statuses),
                random.randint(1, 5),
                random.randint(1, 20)
            )
        )
    return rows


def insert_tasks(rows):
    with get_postgres_conn_cursor() as (_, cur):
        start = time.time()
        cur.executemany(
            """
            INSERT INTO task (title, status, priority, estimated_hours)
            VALUES (%s, %s, %s, %s);
            """,
            rows
        )
        end = time.time()
        elapsed_ms = (end - start) * 1000
        print(f"⏱ Insert rows into Postgres executed in {elapsed_ms:.2f} ms")
        return elapsed_ms


def generate_random_tasks(n=10000):
    rows = build_random_task_rows(n)
    insert_tasks(rows)


# =========================================================
# DEMO AGGREGATE FUNCTION
# =========================================================

def get_max_completed_hours():
    with get_postgres_conn_cursor() as (_, cur):
        # PSEUDO QUERY:
        # LOOK ONLY AT completed TASKS
        # THEN FIND THE LARGEST estimated_hours VALUE
        elapsed_ms = timed_postgres_execute(
            cur,
            """
            SELECT MAX(estimated_hours)
            FROM task
            WHERE status = 'completed';
            """,
            label="Postgres MAX completed"
        )
        rows = cur.fetchall()
        print("Postgres result:")
        print_rows(rows)
        return rows, elapsed_ms


# =========================================================
# ADDITIONAL AGGREGATE FUNCTIONS
# NOTE:
# THESE FIVE FUNCTIONS ONLY CONTAIN DESCRIPTIONS, NOT REAL SQL.
# KEEP THEM COMMENTED OUT IN main UNTIL YOU REPLACE THE TEXT
# WITH REAL SQL STATEMENTS.
# =========================================================

def get_min_priority():
    with get_postgres_conn_cursor() as (_, cur):
        # PSEUDO QUERY:
        # FIND THE SMALLEST priority VALUE AMONG ALL TASKS
        elapsed_ms = timed_postgres_execute(
            cur,
            """
            find the smallest priority value among all tasks
            """,
            label="Postgres MIN priority"
        )
        rows = cur.fetchall()
        print("Postgres result:")
        print_rows(rows)
        return rows, elapsed_ms


def get_avg_estimated_hours():
    with get_postgres_conn_cursor() as (_, cur):
        # PSEUDO QUERY:
        # FIND THE AVERAGE estimated_hours VALUE AMONG ALL TASKS
        elapsed_ms = timed_postgres_execute(
            cur,
            """
            find the average estimated_hours value among all tasks
            """,
            label="Postgres AVG estimated_hours"
        )
        rows = cur.fetchall()
        print("Postgres result:")
        print_rows(rows)
        return rows, elapsed_ms


def get_count_completed_tasks():
    with get_postgres_conn_cursor() as (_, cur):
        # PSEUDO QUERY:
        # COUNT HOW MANY TASKS HAVE status EQUAL TO completed
        elapsed_ms = timed_postgres_execute(
            cur,
            """
            SELECT COUNT(*) FROM Task WHERE status = 'completed';
            """,
            label="Postgres COUNT completed"
        )
        rows = cur.fetchall()
        print("Postgres result:")
        print_rows(rows)
        return rows, elapsed_ms


def get_sum_estimated_hours_completed():
    with get_postgres_conn_cursor() as (_, cur):
        # PSEUDO QUERY:
        # LOOK ONLY AT completed TASKS
        # THEN ADD UP ALL estimated_hours VALUES
        elapsed_ms = timed_postgres_execute(
            cur,
            """
            SELECT SUM(estimated_hours) FROM Task WHERE status = 'completed';
            look only at completed tasks then add up all estimated_hours values
            """,
            label="Postgres SUM completed hours"
        )
        rows = cur.fetchall()
        print("Postgres result:")
        print_rows(rows)
        return rows, elapsed_ms


def get_avg_hours_per_status():
    with get_postgres_conn_cursor() as (_, cur):
        # PSEUDO QUERY:
        # GROUP TASKS BY status
        # THEN FIND THE AVERAGE estimated_hours VALUE FOR EACH GROUP
        elapsed_ms = timed_postgres_execute(
            cur,
            """
            SELECT status, ROUND(AVG(estimated_hours)) FROM task GROUP BY status; 
            group tasks by status then find the average estimated_hours value for each group
            """,
            label="Postgres AVG hours per status"
        )
        rows = cur.fetchall()
        print("Postgres result:")
        print_rows(rows)
        return rows, elapsed_ms


def get_count_tasks_per_priority():
    with get_postgres_conn_cursor() as (_, cur):
        # PSEUDO QUERY:
        # GROUP TASKS BY priority
        # THEN COUNT HOW MANY TASKS ARE IN EACH priority GROUP
        elapsed_ms = timed_postgres_execute(
            cur,
            """
            SELECT COUNT(*) FROM TaskGROUP BY priority;
            group tasks by priority then count how many tasks are in each priority group
            """,
            label="Postgres COUNT per priority"
        )
        rows = cur.fetchall()
        print("Postgres result:")
        print_rows(rows)
        return rows, elapsed_ms


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    # -----------------------------------------------------
    # SETUP
    # -----------------------------------------------------
    # IMPORTANT:
    # create_task_table drops and recreates the table each run.
    # This keeps the schema clean for class demos.
    # drop_task_table()

    create_task_table()

    # -----------------------------------------------------
    # DATA GENERATION
    # -----------------------------------------------------
    # Uncomment once to generate rows.
    # generate_random_tasks(1000)

    # -----------------------------------------------------
    # AGGREGATE FUNCTIONS
    # -----------------------------------------------------
    # Only this one is fully implemented with real SQL.
    get_max_completed_hours()

    # The functions below are description-only for students.
    # Leave them commented out until real SQL is written.
    # get_min_priority()
    # get_avg_estimated_hours()
    # get_count_completed_tasks()
    # get_sum_estimated_hours_completed()
    # get_avg_hours_per_status()
    # get_count_tasks_per_priority()

    print("\nTask table is ready.")