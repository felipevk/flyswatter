from sqlalchemy import text, create_engine
import os
from app.core.config import settings


def test_db_ping():
    engine = create_engine(settings.database_url, future=True)
    with engine.connect() as conn:
        assert conn.execute(text("select 1")).scalar() == 1
