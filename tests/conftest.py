import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_user_service, get_wordset_service
from app.core.config import get_settings
from app.main import create_app
from app.models.user import UserCreate, UserRead
from app.models.wordset import WordsetCreate, WordsetRead, WordsetUpdate
from app.services.user import UserAlreadyExistsError, UserNotFoundError
from app.services.wordset import InvalidDifficultyError, WordsetNotFoundError


class FakeUserService:
    def __init__(self) -> None:
        self._users: list[UserRead] = []
        self._next_id = 1

    def create_user(self, payload: UserCreate) -> UserRead:
        if any(user.email == payload.email for user in self._users):
            raise UserAlreadyExistsError(f"User with email '{payload.email}' already exists.")

        user = UserRead(id=self._next_id, email=payload.email, full_name=payload.full_name)
        self._users.append(user)
        self._next_id += 1
        return user

    def get_user(self, user_id: int) -> UserRead:
        for user in self._users:
            if user.id == user_id:
                return user

        raise UserNotFoundError(f"User with id '{user_id}' was not found.")

    def list_users(self) -> list[UserRead]:
        return list(self._users)


class FakeWordsetService:
    def __init__(self) -> None:
        self._wordsets: list[WordsetRead] = []
        self._next_id = 1
        self._difficulty_ids = {1, 2, 3}

    def create_wordset(self, payload: WordsetCreate) -> WordsetRead:
        self._ensure_valid_difficulty(payload.difficulty)

        wordset = WordsetRead(
            id=self._next_id,
            category=payload.category,
            difficulty=payload.difficulty,
            words=list(payload.words),
        )
        self._wordsets.append(wordset)
        self._next_id += 1
        return wordset

    def get_wordset(self, wordset_id: int) -> WordsetRead:
        for wordset in self._wordsets:
            if wordset.id == wordset_id:
                return wordset

        raise WordsetNotFoundError(f"Wordset with id '{wordset_id}' was not found.")

    def list_wordsets(self) -> list[WordsetRead]:
        return list(self._wordsets)

    def update_wordset(self, wordset_id: int, payload: WordsetUpdate) -> WordsetRead:
        self._ensure_valid_difficulty(payload.difficulty)

        for index, wordset in enumerate(self._wordsets):
            if wordset.id == wordset_id:
                updated_wordset = WordsetRead(
                    id=wordset_id,
                    category=payload.category,
                    difficulty=payload.difficulty,
                    words=list(payload.words),
                )
                self._wordsets[index] = updated_wordset
                return updated_wordset

        raise WordsetNotFoundError(f"Wordset with id '{wordset_id}' was not found.")

    def delete_wordset(self, wordset_id: int) -> None:
        for index, wordset in enumerate(self._wordsets):
            if wordset.id == wordset_id:
                del self._wordsets[index]
                return

        raise WordsetNotFoundError(f"Wordset with id '{wordset_id}' was not found.")

    def _ensure_valid_difficulty(self, difficulty_id: int) -> None:
        if difficulty_id not in self._difficulty_ids:
            raise InvalidDifficultyError(f"Difficulty with id '{difficulty_id}' was not found.")


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("APP_NAME", "KonnectionZ Test API")
    monkeypatch.setenv("SKIP_DB_INIT", "1")
    get_settings.cache_clear()

    app = create_app()
    fake_user_service = FakeUserService()
    fake_wordset_service = FakeWordsetService()
    app.dependency_overrides[get_user_service] = lambda: fake_user_service
    app.dependency_overrides[get_wordset_service] = lambda: fake_wordset_service
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    get_settings.cache_clear()
