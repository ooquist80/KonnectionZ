import jwt
from fastapi import HTTPException
from fastapi.security import SecurityScopes
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pymysql import IntegrityError
from starlette import status

from app.db.client import DatabaseClient
from app.core.config import get_settings
from app.models.token import TokenData
from app.models.user import UserRead, UserNotFoundError, UserWrite, UserRecord
from app.repositories.user_repository import UserRepository


class UserService:

    def __init__(self, database_client: DatabaseClient) -> None:
        self.user_repository = UserRepository(database_client)
        self.password_hasher = PasswordHash.recommended()
        self.settings = get_settings()

    def create(self, user_write: UserWrite) -> UserRead | None:
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
        except Exception as error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An unexpected error occurred while creating the user.") from error
        else:
            return created_user

    def get_by_id(self, user_id: int) -> UserRead:
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User with id: {user_id} was not found.")
        return user

    def get_current_user(self, required_scopes: SecurityScopes, token: str) -> UserRecord:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            decoded_token = jwt.decode(token, self.settings.access_token_auth_key,
                                 algorithms=[self.settings.access_token_algorithm])
            username: str = decoded_token.get("sub")
            if username is None:
                raise credentials_exception
            token_scopes: list[str] = decoded_token.get("scopes", "").split(" ")
            token_data = TokenData(scopes=token_scopes, username=username)
        except InvalidTokenError:
            raise credentials_exception
        user_record = self.user_repository.get_by_username(username)
        if user_record is None:
            raise credentials_exception
        for scope in required_scopes.scopes:
            if scope not in token_data.scopes or scope not in user_record.scopes:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": f'Bearer scope="{scope}"'},
                )
        return user_record

    def get_all(self) -> list[UserRead]:
        return self.user_repository.get_all()

    def delete(self, user_id):
        self.user_repository.delete(user_id)

    def update(self, user_id: int, user_write: UserWrite, change_password: bool):
        hashed_password = self.password_hasher.hash(user_write.password)
        try:
            updated_user = self.user_repository.update_by_id(user_id, user_write, hashed_password, change_password)
        except IntegrityError as error:
            if error.args[0] == 1062 and "for key 'username'" in error.args[1]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"User with username: {user_write.username} already exists.") from error
            elif error.args[0] == 1062 and "for key 'email'" in error.args[1]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"User with email: {user_write.email} already exists.") from error
        except Exception as error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An unexpected error occurred while creating the user.") from error
        else:
            return updated_user

    def update_avatar(self, user_id: int, avatar: str):
        try:
            self.user_repository.update_avatar(user_id, avatar)
        except UserNotFoundError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


