from app.repositories.wordset import WordsetRepository
from app.models.wordset import WordsetRead, WordsetNotFoundError, WordsetWrite
from app.db.client import DatabaseClient


class InvalidDifficultyError(Exception):
    pass


class WordsetService:

    def __init__(self, database_client: DatabaseClient) -> None:
        self.wordset_repository = WordsetRepository(database_client)

    def create_wordset(self, wordset_write: WordsetWrite) -> WordsetRead:
        self._ensure_valid_difficulty(wordset_write.difficulty)
        created_wordset = self.wordset_repository.create(wordset_write)
        return created_wordset

    def get_wordset(self, wordset_id: int) -> WordsetRead:
        wordset = self.wordset_repository.get_by_id(wordset_id)
        if wordset is None:
            raise WordsetNotFoundError(f"Wordset with id '{wordset_id}' was not found.")

        return wordset

    def get_all_wordsets(self) -> list[WordsetRead]:
        return self.wordset_repository.get_all()

    def delete_wordset(self, wordset_id: int) -> None:
        deleted = self.wordset_repository.delete(wordset_id)
        if not deleted:
            raise WordsetNotFoundError(f"Wordset with id '{wordset_id}' was not found.")

    def _ensure_valid_difficulty(self, difficulty_id: int) -> None:
        if not self.wordset_repository.difficulty_exists(difficulty_id):
            raise InvalidDifficultyError(f"Difficulty with id '{difficulty_id}' was not found.")

    def update_wordset(self, wordset_id, payload):
        pass
