import logging
from datetime import timedelta, datetime, timezone

import jwt
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from app.api.deps import verify_password
from app.core.config import get_settings
from app.models.token import Token
from ..db.client import DatabaseClient
from ..repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
settings = get_settings()


class AuthService:

    def __init__(self, database_client: DatabaseClient) -> None:
        self.user_repository = UserRepository(database_client)

    def login(self, username: str, password: str, scopes: str) -> Token:
        user = self.authenticate_user(username, password)
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Incorrect username or password",
                                headers={"WWW-Authenticate": "Bearer"})
        access_token_expires = timedelta(minutes=settings.access_token_expires_in)
        access_token = self.create_access_token(
            data={"sub": username}, scopes=scopes, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")

    def authenticate_user(self, username: str, password: str):
        try:
            user_record = self.user_repository.get_by_username(username)
        except Exception as e:
            logger.error(f"Error while authenticating user {username}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if user_record is None:
            return False
        if not verify_password(password, user_record.password):
            return False
        return user_record

    def create_access_token(self, data: dict, scopes, expires_delta: timedelta):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire, "scopes": " ".join(scopes)})
        encoded_jwt = jwt.encode(to_encode, settings.access_token_auth_key, algorithm=settings.access_token_algorithm)
        return encoded_jwt
