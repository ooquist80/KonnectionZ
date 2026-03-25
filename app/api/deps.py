from fastapi import Depends

from app.core.config import Settings, get_settings
from app.db.client import DatabaseClient


def get_database_client(settings: Settings = Depends(get_settings)) -> DatabaseClient:
    return DatabaseClient(settings)
