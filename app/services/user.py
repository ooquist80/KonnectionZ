from app.repositories.user import UserRepository
from app.models.user import User, UserNotFoundError
from pwdlib import PasswordHash


class UserService:

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def create_user(self, payload: User) -> User:
        password_hasher = PasswordHash.recommended()
        hashed_password = password_hasher.hash(payload.password)
        created_user = self.user_repository.create(email=payload.email, username=payload.username, password=hashed_password)
        return created_user

    def get_user(self, user_id: int) -> User:
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User with id: {user_id} was not found.")
        return user