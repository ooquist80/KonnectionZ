from datetime import timedelta, datetime, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from pymysql import IntegrityError
from starlette import status

from app.repositories.user import UserRepository
from app.models.user import UserRead, UserNotFoundError, UserWrite, UserRecord
from app.models.token import Token, TokenData
from app.db.client import DatabaseClient
from pwdlib import PasswordHash

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create with 'openssl rand -hex 32'
SECRET_KEY = "c083e980e6a9a9a5a9d9ed274c2a6120b9e05335a87f37649bf259885177f4c8"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class UserService:

    def __init__(self, database_client: DatabaseClient) -> None:
        self.user_repository = UserRepository(database_client)
        self.password_hasher = PasswordHash.recommended()

    def create_user(self, user_write: UserWrite) -> UserRead:
        hashed_password = self.password_hasher.hash(user_write.password)
        try:
            created_user = self.user_repository.create(user_write, hashed_password)
        except IntegrityError as error:
            if error.args[0] == 1062 and "for key 'username'" in error.args[1]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"User with username: {user_write.username} already exists.") from error
            elif error.args[0] == 1062 and "for key 'email'" in error.args[1]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"User with email: {user_write.email} already exists.") from error
        except:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An unexpected error occurred while creating the user.") from error


        return created_user

    def get_user_by_id(self, user_id: int) -> UserRead:
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User with id: {user_id} was not found.")
        return user

    def get_user_by_username(self, username: str) -> UserRecord:
        user_record = self.user_repository.get_by_username(username)
        if user_record is None:
            raise UserNotFoundError(f"User with username: {username} was not found.")
        return user_record

    def get_current_user(self, token: str) -> UserRecord:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except InvalidTokenError:
            raise credentials_exception
        user = self.user_repository.get_by_username(username)
        if user is None:
            raise credentials_exception
        return user

    def login(self, username: str, password: str) -> Token:
        user = self.authenticate_user(username, password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect username or password",
                                headers={"WWW-Authenticate": "Bearer"})
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")


    def authenticate_user(self, username: str, password: str):
        try:
            user_record = self.get_user_by_username(username)
        except UserNotFoundError:
            return False
        if not self.password_hasher.verify(password, user_record.password):
            return False
        return user_record


    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

