from datetime import datetime, timezone
import time
from app.models.db import get_conn

def process_transaction(transaction_id: str):
    time.sleep(30)
    
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """UPDATE transactions SET status = 'PROCESSED', processed_at = %s WHERE transaction_id = %s AND status != 'PROCESSED'""",
            (datetime.now(timezone.utc), transaction_id)
        )