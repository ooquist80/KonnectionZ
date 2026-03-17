from app.repositories.wordset import WordsetRepository
from app.models.wordset import Wordset, WordsetNotFoundError




class InvalidDifficultyError(Exception):
    pass

class WordsetService:
    def __init__(self, wordset_repository: WordsetRepository) -> None:
        self.wordset_repository = wordset_repository

    def create_wordset(self, payload: Wordset) -> Wordset:
        self._ensure_valid_difficulty(payload.difficulty)
        created_wordset = self.wordset_repository.create(
            category=payload.category,
            difficulty=payload.difficulty,
            words=payload.words,
        )
        return created_wordset

    def get_wordset(self, wordset_id: int) -> Wordset:
        wordset = self.wordset_repository.get_by_id(wordset_id)
        if wordset is None:
            raise WordsetNotFoundError(f"Wordset with id '{wordset_id}' was not found.")

        return wordset

    def get_all_wordsets(self) -> list[Wordset]:
        return self.wordset_repository.get_all()

    def delete_wordset(self, wordset_id: int) -> None:
        deleted = self.wordset_repository.delete(wordset_id)
        if not deleted:
            raise WordsetNotFoundError(f"Wordset with id '{wordset_id}' was not found.")

    def _ensure_valid_difficulty(self, difficulty_id: int) -> None:
        if not self.wordset_repository.difficulty_exists(difficulty_id):
            raise InvalidDifficultyError(f"Difficulty with id '{difficulty_id}' was not found.")

