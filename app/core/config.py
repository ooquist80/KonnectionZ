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
    access_token_auth_key : str
    access_token_expires_in : int
    access_token_algorithm : str
    allowed_origins : list[str]
    environment: str


def _as_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "KonnectionZ API"),
        environment=os.getenv("ENVIRONMENT", "development"),
        database_host=os.getenv("DB_HOST", "127.0.0.1"),
        database_port=int(os.getenv("DB_PORT", "3306")),
        database_user=os.getenv("DB_USER", "root"),
        database_password=os.getenv("DB_PASSWORD", "password"),
        database_name=os.getenv("DB_NAME", "konnectionz"),
        skip_db_init=_as_bool(os.getenv("SKIP_DB_INIT")),
        # Create with 'openssl rand -hex 32'
        access_token_auth_key=os.getenv("ACCESS_TOKEN_AUTH_KEY",
                                        "c083e980e6a9a9a5a9d9ed274c2a6120b9e05335a87f37649bf259885177f4c8"),
        access_token_expires_in=int(os.getenv("ACCESS_TOKEN_EXPIRES_IN", 60*12)),
        access_token_algorithm=os.getenv("ACCESS_TOKEN_ALGORITHM","HS256"),
        allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://192.168.0.5:5173").split(",")
    )
