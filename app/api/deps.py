from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.config import Settings, get_settings
from app.db.client import DatabaseClient
from app.services.user import UserService
from app.models.user import UserRead

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

def get_database_client(settings: Settings = Depends(get_settings)) -> DatabaseClient:
    return DatabaseClient(settings)

def get_user_service(database_client: DatabaseClient = Depends(get_database_client)) -> UserService:
    return UserService(database_client)

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                     user_service: Annotated[UserService, Depends(get_user_service)]) -> UserRead:
    user_record = user_service.get_current_user(token)
    return UserRead(id=user_record.id, username=user_record.username, email=user_record.email,
                    scopes=user_record.scopes)



