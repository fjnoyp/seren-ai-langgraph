import os
from contextlib import contextmanager
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


use_dev_pool = True

if use_dev_pool:
    os.environ["POSTGRES_HOST"] = "localhost"
    os.environ["POSTGRES_DATABASE"] = "postgres"
    os.environ["POSTGRES_USER"] = "postgres"
    os.environ["POSTGRES_PASSWORD"] = "postgres"
    os.environ["POSTGRES_PORT"] = "54322"

# Create a global connection pool
pool = SimpleConnectionPool(
    minconn=1,          # Minimum connections in pool
    maxconn=10,         # Maximum connections in pool
    host=os.environ.get("POSTGRES_HOST"),
    database=os.environ.get("POSTGRES_DATABASE"),
    user=os.environ.get("POSTGRES_USER"),
    password=os.environ.get("POSTGRES_PASSWORD"),
    port=os.environ.get("POSTGRES_PORT", 5432)
)


@contextmanager
def get_db_connection():
    """
    Context manager that handles getting and returning connections to the pool
    """
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)

def execute_query(query: str, params: dict = None):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchall()

# Make sure to clean up the pool when shutting down
def cleanup():
    if pool:
        pool.closeall() 