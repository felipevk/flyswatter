from sqlalchemy import create_engine
from app.core.config import settings
from sqlalchemy_utils import database_exists, create_database

if __name__ == "__main__":
    engine = create_engine(settings.database_url, future=True)
    if not database_exists(engine.url):
        create_database(engine.url)