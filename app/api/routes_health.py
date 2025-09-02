from fastapi import APIRouter
from sqlalchemy import text
from app.db.session import engine

router = APIRouter(tags=["health"])

@router.get("/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("select 1"))
    return {"status": "ok"}