from pydantic_settings import BaseSettings
from functools import lru_cache
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class Settings(BaseSettings):
    APP_NAME: str = "AI Rapor Sistemi"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = f"sqlite+aiosqlite:///{os.path.join(BASE_DIR, 'database', 'ai_rapor.db')}"

    SECRET_KEY: str = "super-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    REPORTS_DIR: str = os.path.join(BASE_DIR, "reports", "generated")
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024

    N8N_WEBHOOK_URL: str = "http://localhost:5678/webhook"
    N8N_API_URL: str = "http://localhost:5678/api/v1"

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
