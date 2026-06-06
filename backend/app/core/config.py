"""
core/config.py
==============
Centralized application settings via pydantic-settings.
All values can be overridden by environment variables or the .env file.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Application ---
    APP_NAME: str = "VendorBridge ERP"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # --- Database ---
    DATABASE_URL: str = (
        "postgresql+asyncpg://vendorbridge:vendorbridge@postgres:5432/vendorbridge"
    )

    # --- JWT Authentication ---
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Email (SMTP) ---
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # --- CORS ---
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
