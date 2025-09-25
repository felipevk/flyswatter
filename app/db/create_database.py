from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists

from app.core.config import settings

if __name__ == "__main__":
    create_db()

def create_db():
    print(f"Creating db at {settings.database_url}")
    engine = create_engine(settings.database_url, future=True)
    if not database_exists(engine.url):
        create_database(engine.url)