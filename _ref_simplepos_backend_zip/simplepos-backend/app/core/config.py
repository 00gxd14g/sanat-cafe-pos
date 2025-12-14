from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the self-hosted POS backend."""

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # App
    APP_NAME: str = 'OzluceSanat POS Backend'
    ENV: str = 'dev'  # dev|prod
    TZ: str = 'Europe/Istanbul'

    # DB
    DATABASE_URL: str = 'sqlite:///./pos.db'

    # CORS
    CORS_ALLOW_ORIGINS: str = 'http://localhost:5173,http://127.0.0.1:5173'

    # Printing
    RUN_PRINT_WORKER: bool = True
    PRINT_POLL_SECONDS: float = 0.8
    PRINT_MAX_ATTEMPTS: int = 3

    # Default printer names (must match Windows printer names)
    PRINTER_KITCHEN_NAME: str = 'POS-58'
    PRINTER_CUSTOMER_NAME: str = 'POS-58'

    # Receipt formatting
    RECEIPT_LINE_WIDTH: int = 32  # typical for 58mm
    RECEIPT_ENCODING: str = 'cp857'  # Turkish-friendly; adjust if needed


settings = Settings()
