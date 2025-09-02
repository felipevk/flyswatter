from sqlalchemy import text, create_engine
import os

def test_db_ping():
    engine = create_engine(os.getenv("DATABASE_URL"), future=True)
    with engine.connect() as conn:
        assert conn.execute(text("select 1")).scalar() == 1