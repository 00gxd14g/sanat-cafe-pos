from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "backend/.env"), env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./pos.db"
    tz: str = "Europe/Istanbul"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    print_mode: str = "file"  # spooler|file|noop
    print_output_dir: str = "./prints"
    print_worker_in_app: bool = False

    printer_kitchen_name: str = ""
    printer_customer_name: str = ""
    kitchen_show_prices: bool = False
    customer_show_prices: bool = True

    print_strategy: str = "server"  # qz|server
    qz_public_cert_path: str = "backend/keys/public-cert.pem"
    qz_private_key_path: str = "backend/keys/private-key.pem"
    qz_encoding: str = "CP857"

    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
