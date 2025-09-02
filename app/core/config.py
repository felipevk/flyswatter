from pydantic import BaseModel
import os

class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL", "")

settings = Settings()