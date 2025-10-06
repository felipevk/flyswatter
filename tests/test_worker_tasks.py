from datetime import datetime

from sqlalchemy import insert, select
from uuid import uuid4

from app.core.config import settings
from app.db.models import User, Job, JobState, JobResultKind
from app.db.factory import create_user, create_project, create_issue, create_job

from .conftest import db_session

from app.core.errors import BlobError

from .test_routes_common import get_test_token

from app.api.dto import UserReport

from fastapi.testclient import TestClient

def test_generatereport_success(db_session, mockMinIO, monkeypatch):
    import app.worker.tasks as tasks
    monkeypatch.setattr(tasks, "create_session", lambda: db_session)
    login = "jdoetestuser"
    password = "AAAAAAA"
    userDB = create_user(username=login, password=password)
    db_session.add(userDB)
    projectDB = create_project(userDB)
    db_session.add(projectDB)
    db_session.add(create_issue(projectDB, userDB, userDB))
    jobDB = create_job(
            userDB, 
            job_type="generate-report",
            idempotency_key = uuid4().hex
        )
    db_session.add(jobDB)
    db_session.commit()

    tasks.generate_report.delay(jobDB.public_id, userDB.public_id)
    db_session.refresh(jobDB)

    assert jobDB.state == JobState.SUCCEEDED
    assert jobDB.result_kind == JobResultKind.ARTIFACT