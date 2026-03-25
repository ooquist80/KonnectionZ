import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    app_name: str
    database_host: str
    database_port: int
    database_user: str
    database_password: str
    database_name: str
    skip_db_init: bool


def _as_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "KonnectionZ API"),
        database_host=os.getenv("DB_HOST", "127.0.0.1"),
        database_port=int(os.getenv("DB_PORT", "3306")),
        database_user=os.getenv("DB_USER", "root"),
        database_password=os.getenv("DB_PASSWORD", "password"),
        database_name=os.getenv("DB_NAME", "konnectionz"),
        skip_db_init=_as_bool(os.getenv("SKIP_DB_INIT")),
    )
