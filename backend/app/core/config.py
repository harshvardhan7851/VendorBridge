"""
Application Settings
====================
Centralized configuration using pydantic-settings.
Values are read from environment variables (or .env file).
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    All application settings.
    Override any field by setting the corresponding environment variable.
    """

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
    """
    Returns a cached Settings instance.
    Use as a FastAPI dependency: settings = Depends(get_settings)
    """
    return Settings()


# Module-level singleton for convenience
settings = get_settings()
