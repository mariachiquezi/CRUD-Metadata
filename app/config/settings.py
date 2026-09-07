import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@dataclass
class Settings:
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    mongodb_db_name: str = os.getenv("MONGODB_DB_NAME", "catalog_metadata")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    def validate(self) -> None:
        if not self.mongodb_uri.strip():
            raise RuntimeError("Configure MONGODB_URI no ambiente ou em app/.env.")
        if not self.mongodb_db_name.strip():
            raise RuntimeError("Configure MONGODB_DB_NAME no ambiente ou em app/.env.")
        if len(self.jwt_secret_key.encode("utf-8")) < 32:
            raise RuntimeError("Configure JWT_SECRET_KEY com pelo menos 32 bytes em app/.env.")
        if self.access_token_expire_minutes <= 0:
            raise RuntimeError("access_token_expire_minutes deve ser maior que zero.")


settings = Settings()


MAX_BULK_FILES = 10
MAX_FILE_SIZE = 5 * 1024 * 1024
