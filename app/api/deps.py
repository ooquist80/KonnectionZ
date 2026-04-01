from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from pwdlib import PasswordHash

from app.core.config import Settings, get_settings
from app.db.client import DatabaseClient
from app.models.user import UserRead
from app.services.user import UserService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    scopes={"user:play": "Can play games", "user:admin": "Can administer games"}
)

password_hasher = PasswordHash.recommended()

def get_database_client(settings: Settings = Depends(get_settings)) -> DatabaseClient:
    return DatabaseClient(settings)


def get_user_service(database_client: DatabaseClient = Depends(get_database_client)) -> UserService:
    return UserService(database_client)


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                     user_service: Annotated[UserService, Depends(get_user_service)],
                     security_scopes: SecurityScopes) -> UserRead:
    user_record = user_service.get_current_user(security_scopes, token)
    return UserRead(id=user_record.id, username=user_record.username, email=user_record.email,
                    scopes=user_record.scopes)

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hasher.verify(plain_password, hashed_password)
