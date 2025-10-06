from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database.build_url(), pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def create_session() -> Session:
    return SessionLocal()
