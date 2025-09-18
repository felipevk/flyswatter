import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db.base import Base  # your declarative Base
from app.core.config import settings
import subprocess

TEST_DB_URL = settings.database_url

@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    # Run Alembic migrations once for the test DB
    subprocess.run(
        ["alembic", "upgrade", "head"],
        check=True,
        env={**os.environ, "DATABASE_URL": TEST_DB_URL},
    )

    yield  # tests run after this
    subprocess.run(
            ["alembic", "downgrade", "base"],
            check=True,
            env={**os.environ, "DATABASE_URL": TEST_DB_URL},
        )

@pytest.fixture(scope="session")
def connection():
    engine = create_engine(TEST_DB_URL, future=True)
    # Keep one DB connection for the whole test session
    with engine.connect() as conn:
        yield conn

@pytest.fixture(autouse=True)
def db_session(connection):
    trans = connection.begin()         # BEGIN
    Session = sessionmaker(bind=connection, expire_on_commit=False, future=True)
    testSession = Session()
    
    def get_session_override() -> Session:
        return testSession
 
    #app.dependency_overrides[get_session] = get_session_override

    # Start a SAVEPOINT so the Session can use nested transactions
    nested = connection.begin_nested()

    try:
        yield testSession
    finally:
        testSession.close()
        nested.close()
        trans.rollback()               # ROLLBACK
        