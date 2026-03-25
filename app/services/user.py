from app.repositories.user import UserRepository
from app.models.user import User, UserNotFoundError
from app.db.client import DatabaseClient
import bcrypt


class UserService:

    def __init__(self, database_client : DatabaseClient) -> None:
        self.user_repository = UserRepository(database_client)

    def create_user(self, payload: User) -> User:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(payload.password.encode('utf-8'), salt)
        created_user = self.user_repository.create(email=payload.email, username=payload.username, password=hashed_password)
        return created_user

    def get_user(self, user_id: int) -> User:
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User with id: {user_id} was not found.")
        return user