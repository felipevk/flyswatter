import os
import subprocess
import sys
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists

from app.api.routes_common import get_session
from app.core.config import settings
from app.core.errors import BlobError
from app.db.base import Base  # your declarative Base
from app.main import app
from app.worker.celery_app import app as celery_app

TEST_DB_URL = settings.database.build_url()


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    # Run Alembic migrations once for the test DB
    try:
        upgrade = subprocess.run(
            ["poetry", "run", "alembic", "upgrade", "head"],
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
            ["poetry", "run", "alembic", "downgrade", "base"],
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
def connection(apply_migrations):
    engine = create_engine(TEST_DB_URL, future=True)

    # Keep ONE DB connection open for the whole test session.
    with engine.connect() as conn:
        yield conn


@pytest.fixture(autouse=True)
def db_session(connection):
    # In order to keep test transactions isolated
    # We start a test wide transaction that should remain open until the end of the test
    # However, session.commit() ends a transaction, so we need to wrap the test between
    # a nested sub transaction, and restart every time session.commit() is called
    # Once the test is over we can rollback the test wide transaction

    trans = connection.begin()  # BEGIN

    # Start a SAVEPOINT so the Session can use nested transactions
    nested = connection.begin_nested()

    Session = sessionmaker(bind=connection, expire_on_commit=False, future=True)
    testSession = Session()

    # Listen to transaction end, ie session.commit()
    # re-establish the SAVEPOINT so subsequent work is still isolated.
    @event.listens_for(testSession, "after_transaction_end")
    def _restart_savepoint(sess, trans_):
        if not connection.in_nested_transaction():
            connection.begin_nested()

    try:
        yield testSession
    finally:
        testSession.close()
        try:
            nested.close()
        except Exception:
            pass
        # ROLLBACK
        trans.rollback()
        app.dependency_overrides.pop(get_session, None)


@pytest.fixture(autouse=True)
def override_db_session(db_session):
    def _override():
        return db_session

    app.dependency_overrides[get_session] = _override
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_session, None)


@pytest.fixture
def mockMinIO():
    with patch("app.blob.storage.Minio") as mockMinio:
        mockMinio.return_value.presigned_get_object.return_value = "Mock.pdf"
        yield mockMinIO


@pytest.fixture
def mockMinIOFailure():
    with patch("app.blob.storage.Minio") as mockMinio:
        mockMinio.return_value.presigned_get_object.side_effect = BlobError
        yield mockMinIO


@pytest.fixture(scope="session", autouse=True)
def celery_conf():
    celery_app.conf.update(
        task_always_eager=True,  # run inline
        task_eager_propagates=True,  # raise exceptions to pytest
        task_ignore_result=True,  # don't touch result backend
        task_store_eager_result=False,  # belt & suspenders
        broker_url="memory://",  # no Redis/Rabbit sockets/threads
        broker_connection_retry_on_startup=False,
    )
    yield
