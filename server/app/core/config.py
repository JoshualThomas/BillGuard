import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "BillGuard API"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "default-insecure-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/billguard"
    
    # AI Engine
    GEMINI_API_KEY: Optional[str] = None
    
    # Notifications - Resend Email
    RESEND_API_KEY: Optional[str] = None
    EMAIL_FROM: str = "BillGuard <alerts@billguard.app>"
    
    # Notifications - Telegram Bot
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    
    # URLs for Magic Links & Webhooks
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
