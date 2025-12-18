import time
import psycopg
from app.models.db import get_conn

def init_db(retries: int = 10, delay: int = 2):
    for attempt in range(retries):
        try:
            with get_conn() as conn:
                conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id TEXT PRIMARY KEY,
                    source_account TEXT,
                    destination_account TEXT,
                    amount INTEGER,
                    currency TEXT,
                    status TEXT,
                    created_at TIMESTAMP,
                    processed_at TIMESTAMP
                )
                """)
            print("Database is ready")
            return
        except psycopg.OperationalError:
            print(f"Waiting for Postgres... ({attempt + 1}/{retries})")
            time.sleep(delay)

    raise RuntimeError("Database not ready after retries")
