from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.repositories.user import UserRepository
from app.models.user import UserRead, UserNotFoundError, UserWrite, UserRecord
from app.db.client import DatabaseClient
import bcrypt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserService:

    def __init__(self, database_client: DatabaseClient) -> None:
        self.user_repository = UserRepository(database_client)

    def create_user(self, user_write: UserWrite) -> UserRead:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(user_write.password.encode('utf-8'), salt)
        created_user = self.user_repository.create(user_write, hashed_password)
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

    def get_current_user(self, token: str) -> UserRead:
        if token == "lol":
            return self.get_user_by_id(1)
        else:
            raise Exception("Invalid token")

    def login(self, username: str, password: str):
        try:
            user_record = self.get_user_by_username(username)
        except UserNotFoundError:
            raise HTTPException(status_code=400, detail="Incorrect username or password")

        if user_record and bcrypt.checkpw(password.encode('utf-8'), user_record.password.encode('utf-8')):
            return {"access_token": user_record.username, "token_type": "bearer" }
        else:
            raise HTTPException(status_code=400, detail="Incorrect username or password")

