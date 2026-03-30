from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.config import Settings, get_settings
from app.db.client import DatabaseClient

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_database_client(settings: Settings = Depends(get_settings)) -> DatabaseClient:
    return DatabaseClient(settings)





