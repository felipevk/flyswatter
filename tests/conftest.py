import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db.base import Base  # your declarative Base
from app.core.config import settings
import subprocess, os, sys

TEST_DB_URL = settings.database_url

@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    # Run Alembic migrations once for the test DB
    try:
        upgrade = subprocess.run(
            ["alembic", "upgrade", "head"],
            check=True,
            env={**os.environ, "DATABASE_URL": TEST_DB_URL},
        )
        print(upgrade.stdout)
    except subprocess.CalledProcessError as e:
        print("\n[ALEMBIC CMD]", e.cmd, file=sys.stderr)
        print("\n[STDOUT]\n", e.stdout, file=sys.stderr)
        print("\n[STDERR]\n", e.stderr, file=sys.stderr)
        raise

    yield  # tests run after this
    try:
        downgrade = subprocess.run(
                ["alembic", "downgrade", "base"],
                check=True,
                env={**os.environ, "DATABASE_URL": TEST_DB_URL},
            )
        print(downgrade.stdout)
    except subprocess.CalledProcessError as e:
        print("\n[ALEMBIC CMD]", e.cmd, file=sys.stderr)
        print("\n[STDOUT]\n", e.stdout, file=sys.stderr)
        print("\n[STDERR]\n", e.stderr, file=sys.stderr)
        raise


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
        