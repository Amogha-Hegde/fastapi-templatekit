from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "$project_name"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
