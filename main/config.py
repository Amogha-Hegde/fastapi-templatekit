from dataclasses import dataclass
from os import getenv


def _get_bool(name: str, default: bool = False) -> bool:
    value = getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = getenv("APP_NAME", "FastAPI Template")
    app_version: str = getenv("APP_VERSION", "0.1.0")
    api_prefix: str = getenv("API_PREFIX", "/api/v1")
    debug: bool = _get_bool("DEBUG", default=False)


settings = Settings()
