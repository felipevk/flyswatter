import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base  # your declarative Base

TEST_DB_URL = os.getenv("DATABASE_URL")

@pytest.fixture(scope="session", autouse=True)
def setup_schema():
    engine = create_engine(TEST_DB_URL, future=True)
    Base.metadata.create_all(bind=engine)
    yield # tests run here
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()