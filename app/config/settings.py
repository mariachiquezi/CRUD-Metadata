import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@dataclass
class Settings:
    mongodb_uri: str = os.getenv("MONGODB_URI")
    mongodb_db_name: str = os.getenv("MONGODB_DB_NAME")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-this-test-secret")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


settings = Settings()


MAX_BULK_FILES = 10
MAX_FILE_SIZE = 5 * 1024 * 1024