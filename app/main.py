from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from app.models.init_db import init_db
from app.routes.transaction import router as txn_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {
        "status": "Healthy",
        "current_time": datetime.now(timezone.utc).isoformat()
    }

app.include_router(txn_router, prefix="/v1")