from datetime import datetime, timezone
from fastapi import APIRouter, status
from pydantic import BaseModel
from app.models.db import get_conn
from app.services.worker import process_transaction
from app.services.queue import queue

router = APIRouter()

class TransactionWebhook(BaseModel):
    transaction_id: str
    source_account: str
    destination_account: str
    amount: float
    currency: str

@router.post("/webhooks/transactions", status_code=status.HTTP_202_ACCEPTED)
async def receive_webhook(payload: TransactionWebhook):
    with get_conn() as conn:
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM transactions WHERE transaction_id = %s", (payload.transaction_id,))
        if cur.fetchone():
            return
        
        cur.execute("""
        INSERT INTO transactions (
            transaction_id,
            source_account,
            destination_account,
            amount,
            currency,
            status,
            created_at
        ) VALUES(%s, %s, %s, %s, %s, 'PROCESSING', %s)""",
        (payload.transaction_id, payload.source_account, payload.destination_account, payload.amount, payload.currency, datetime.now(timezone.utc))
        )
    
    queue.enqueue(process_transaction, payload.transaction_id)
    
    return {
        "message": "accepted"
    }

@router.get("/transactions/{transaction_id}")
async def get_transaction(transaction_id: str):
    with get_conn() as conn:
        cur = conn.cursor()

        cur.execute("SELECT * FROM transactions WHERE transaction_id = %s", (transaction_id,))
        row = cur.fetchone()
    if not row:
        return []

    keys = ["transaction_id", "source_account", "destination_account", "amount", "currency", "status", "created_at", "processed_at"]

    return [dict(zip(keys, row))]
