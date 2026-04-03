import os
import random
import time
from contextlib import contextmanager

import psycopg2
from dotenv import load_dotenv

load_dotenv()

ENC_KEY = os.getenv("ENC_KEY")

# =========================================================
# DISTRIBUTED DATABASE CONFIG
# =========================================================

def load_database_nodes():
    """
    Reads database node names from DB_NODES and resolves each
    node's connection string from DATABASE_URL_<NODE_NAME>.
    """
    raw_nodes = os.getenv("DB_NODES", "").strip()
    if not raw_nodes:
        raise ValueError("DB_NODES is missing in .env")

    node_names = [node.strip() for node in raw_nodes.split(",") if node.strip()]
    if not node_names:
        raise ValueError("DB_NODES is empty after parsing")

    db_map = {}

    for node in node_names:
        env_key = f"DATABASE_URL_{node.upper()}"
        db_url = os.getenv(env_key)

        if not db_url:
            raise ValueError(f"Missing environment variable: {env_key}")

        db_map[node] = db_url

    return db_map


DATABASE_NODES = load_database_nodes()


def get_available_nodes():
    return list(DATABASE_NODES.keys())


# =========================================================
# CONNECTION
# =========================================================

def _get_conn(node_name):
    if node_name not in DATABASE_NODES:
        raise ValueError(f"Unknown database node: {node_name}")

    return psycopg2.connect(DATABASE_NODES[node_name])


@contextmanager
def get_conn_cursor(node_name):
    conn = _get_conn(node_name)
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


def timed_execute(cur, query, params=None, label="SQL", node_name=None):
    if _is_incomplete_query(query):
        print(f"⏭ Skipping incomplete query: {label}")
        return False

    start = time.time()
    cur.execute(query, params or ())
    end = time.time()

    prefix = f"[{node_name}] " if node_name else ""
    print(f"{prefix}⏱ {label} executed in {(end - start) * 1000:.2f} ms")
    return True


# =========================================================
# TABLE PRINT
# =========================================================

def print_table(rows, headers=None):
    if not rows:
        print("No results.")
        return

    if headers:
        print(" | ".join(headers))

    for row in rows:
        print(row)


# =========================================================
# DISTRIBUTED HELPERS
# =========================================================

def execute_on_node(node_name, query, params=None, label="SQL", fetch=False, fetchone=False):
    with get_conn_cursor(node_name) as (_, cur):
        executed = timed_execute(cur, query, params, label=label, node_name=node_name)
        if not executed:
            return None

        if fetchone:
            return cur.fetchone()

        if fetch:
            return cur.fetchall()

        return True


def execute_on_all_nodes(query, params=None, label="SQL", fetch=False):
    results = {}

    for node_name in get_available_nodes():
        try:
            with get_conn_cursor(node_name) as (_, cur):
                executed = timed_execute(cur, query, params, label=label, node_name=node_name)
                if executed and fetch:
                    results[node_name] = cur.fetchall()
                else:
                    results[node_name] = True
        except Exception as e:
            results[node_name] = f"ERROR: {e}"

    return results


def choose_node_by_user_id(user_id):
    """
    Simple shard selection using modulo.
    A traditional and reliable first step for distribution.
    """
    nodes = get_available_nodes()
    index = user_id % len(nodes)
    return nodes[index]


# =========================================================
# INIT + SEED
# =========================================================

def init_db_all():
    create_user_sql = """
        CREATE TABLE IF NOT EXISTS AppUser (
            id SERIAL PRIMARY KEY,
            name VARCHAR(256) NOT NULL,
            email VARCHAR(256) NOT NULL UNIQUE
        );
    """

    create_task_sql = """
        CREATE TABLE IF NOT EXISTS Task (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title VARCHAR(256) NOT NULL,
            status VARCHAR(50) NOT NULL,
            description TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            reminder_time TIMESTAMPTZ,
            FOREIGN KEY (user_id) REFERENCES AppUser(id) ON DELETE CASCADE
        );
    """

    execute_on_all_nodes(create_user_sql, label="Create AppUser")
    execute_on_all_nodes(create_task_sql, label="Create Task")


def seed_data():
    users = [
        ("Alice", "alice@email.com"),
        ("Bob", "bob@email.com"),
    ]

    for i, (name, email) in enumerate(users, start=1):
        node_name = choose_node_by_user_id(i)
        execute_on_node(
            node_name,
            """
            INSERT INTO AppUser (name, email)
            VALUES (%s, %s)
            ON CONFLICT (email) DO NOTHING;
            """,
            (name, email),
            label="Insert user"
        )


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
        "Prepare presentation"
    ]

    statuses = ["pending", "completed"]

    for _ in range(n):
        user_id = random.randint(1, 1000)
        title = random.choice(titles)
        status = random.choice(statuses)

        node_name = choose_node_by_user_id(user_id)

        execute_on_node(
            node_name,
            """
            INSERT INTO Task (user_id, title, status)
            VALUES (%s, %s, %s);
            """,
            (user_id, title, status),
            label="Insert random task"
        )


# =========================================================
# USER OPERATIONS
# =========================================================

def create_user(name, email):
    """
    Route user to one shard based on a stable hash-like rule.
    """
    pseudo_user_id = abs(hash(email))
    node_name = choose_node_by_user_id(pseudo_user_id)

    execute_on_node(
        node_name,
        """
        INSERT INTO AppUser (name, email)
        VALUES (%s, %s)
        ON CONFLICT (email) DO NOTHING;
        """,
        (name, email),
        label="Create user"
    )


def get_all_users():
    results = execute_on_all_nodes(
        "SELECT id, name, email FROM AppUser;",
        label="Get all users",
        fetch=True
    )

    all_rows = []
    for node_name, rows in results.items():
        if isinstance(rows, list):
            for row in rows:
                all_rows.append((node_name, *row))

    print_table(all_rows, ["node", "id", "name", "email"])
    return all_rows


def get_user_by_id(user_id):
    node_name = choose_node_by_user_id(user_id)

    row = execute_on_node(
        node_name,
        """
        SELECT id, name, email
        FROM AppUser
        WHERE id = %s;
        """,
        (user_id,),
        label="Get user by id",
        fetchone=True
    )

    if row:
        print_table([(node_name, *row)], ["node", "id", "name", "email"])
    else:
        print("No results.")

    return row


# =========================================================
# TASK OPERATIONS
# =========================================================

def create_task(user_id, title, status="pending", description=None):
    node_name = choose_node_by_user_id(user_id)

    execute_on_node(
        node_name,
        """
        INSERT INTO Task (user_id, title, status, description)
        VALUES (%s, %s, %s, %s);
        """,
        (user_id, title, status, description),
        label="Create task"
    )


def get_all_tasks():
    results = execute_on_all_nodes(
        """
        SELECT id, user_id, title, status, description, created_at
        FROM Task;
        """,
        label="Get all tasks",
        fetch=True
    )

    all_rows = []
    for node_name, rows in results.items():
        if isinstance(rows, list):
            for row in rows:
                all_rows.append((node_name, *row))

    print_table(
        all_rows,
        ["node", "id", "user_id", "title", "status", "description", "created_at"]
    )
    return all_rows


def get_tasks_by_user(user_id):
    node_name = choose_node_by_user_id(user_id)

    rows = execute_on_node(
        node_name,
        """
        SELECT id, user_id, title, status, description, created_at
        FROM Task
        WHERE user_id = %s;
        """,
        (user_id,),
        label="Get tasks by user",
        fetch=True
    ) or []

    print_table(rows, ["id", "user_id", "title", "status", "description", "created_at"])
    return rows


def get_completed_tasks():
    results = execute_on_all_nodes(
        """
        SELECT id, user_id, title, status
        FROM Task
        WHERE status = 'completed';
        """,
        label="Get completed tasks",
        fetch=True
    )

    all_rows = []
    for node_name, rows in results.items():
        if isinstance(rows, list):
            for row in rows:
                all_rows.append((node_name, *row))

    print_table(all_rows, ["node", "id", "user_id", "title", "status"])
    return all_rows


def update_task_status(task_id, user_id, status):
    node_name = choose_node_by_user_id(user_id)

    execute_on_node(
        node_name,
        """
        UPDATE Task
        SET status = %s
        WHERE id = %s AND user_id = %s;
        """,
        (status, task_id, user_id),
        label="Update task status"
    )


def delete_task(task_id, user_id):
    node_name = choose_node_by_user_id(user_id)

    execute_on_node(
        node_name,
        """
        DELETE FROM Task
        WHERE id = %s AND user_id = %s;
        """,
        (task_id, user_id),
        label="Delete task"
    )


# =========================================================
# INDEXING
# =========================================================

def create_status_index_all():
    execute_on_all_nodes(
        """
        CREATE INDEX IF NOT EXISTS idx_task_status
        ON Task(status);
        """,
        label="Create status index"
    )


# =========================================================
# ENCRYPT / DECRYPT
# =========================================================

def enable_pgcrypto_all():
    execute_on_all_nodes(
        "CREATE EXTENSION IF NOT EXISTS pgcrypto;",
        label="Enable pgcrypto"
    )


def encrypt_user_email(user_id):
    node_name = choose_node_by_user_id(user_id)

    execute_on_node(
        node_name,
        """
        UPDATE AppUser
        SET email = pgp_sym_encrypt(email, %s)::text
        WHERE id = %s;
        """,
        (ENC_KEY, user_id),
        label="Encrypt user email"
    )


def decrypt_user_email(user_id):
    node_name = choose_node_by_user_id(user_id)

    row = execute_on_node(
        node_name,
        """
        SELECT pgp_sym_decrypt(email::bytea, %s)
        FROM AppUser
        WHERE id = %s;
        """,
        (ENC_KEY, user_id),
        label="Decrypt user email",
        fetchone=True
    )

    print(row)
    return row


# =========================================================
# CURRENT USER
# =========================================================

def get_current_user_all():
    results = execute_on_all_nodes(
        "SELECT current_user;",
        label="Get current user",
        fetch=True
    )

    for node_name, rows in results.items():
        print(f"{node_name}: {rows}")


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    init_db_all()
    # seed_data()
    # generate_random_tasks(1000)
    # create_status_index_all()
    get_all_users()
    print("Distributed app ready.")