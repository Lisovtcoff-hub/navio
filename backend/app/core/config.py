from __future__ import annotations

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Backend configuration.

    All environment variables are prefixed with NAVIO_.
    Example: NAVIO_DEBUG=true
    """

    model_config = SettingsConfigDict(
        env_prefix="NAVIO_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    env: str = "local"
    debug: bool = True
    project_name: str = "Navio API"
    version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]


settings = Settings()
