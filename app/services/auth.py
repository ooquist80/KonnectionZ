from datetime import timedelta, datetime, timezone

import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from app.models.token import Token
from app.models.user import UserNotFoundError
from app.api.deps import verify_password
from .user import UserService
from ..db.client import DatabaseClient
from ..repositories.user import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create with 'openssl rand -hex 32'
SECRET_KEY = "c083e980e6a9a9a5a9d9ed274c2a6120b9e05335a87f37649bf259885177f4c8"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
class AuthService:

    def __init__(self, database_client: DatabaseClient) -> None:
        self.user_repository = UserRepository(database_client)

    def login(self, username: str, password: str, scopes: str) -> Token:
        user = self.authenticate_user(username, password)
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Incorrect username or password",
                                headers={"WWW-Authenticate": "Bearer"})
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": username}, scopes=scopes, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")

    def authenticate_user(self, username: str, password: str):
        try:
            user_record = self.user_repository.get_by_username(username)
        except UserNotFoundError:
            return False
        if not verify_password(password, user_record.password):
            return False
        return user_record

    def create_access_token(self, data: dict, scopes, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire, "scopes": " ".join(scopes)})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

