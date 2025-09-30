from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists

from app.core.config import settings


def create_db():
    print(f"Creating db at {settings.database.build_url()}")
    engine = create_engine(settings.database.build_url(), future=True)
    if not database_exists(engine.url):
        create_database(engine.url)


if __name__ == "__main__":
    create_db()
