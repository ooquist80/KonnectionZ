import logging

from fastapi import HTTPException

from app.db.client import DatabaseClient
from app.models.wordset import WordsetRead, WordsetNotFoundError, WordsetWrite
from app.repositories.wordset_repository import WordsetRepository

logger = logging.getLogger(__name__)

class InvalidDifficultyError(Exception):
    pass


class WordsetService:

    def __init__(self, database_client: DatabaseClient) -> None:
        self.wordset_repository = WordsetRepository(database_client)

    def create_wordset(self, wordset_write: WordsetWrite) -> WordsetRead:
        try:
            self._ensure_valid_difficulty(wordset_write.difficulty)
            created_wordset = self.wordset_repository.create(wordset_write)
            return created_wordset
        except InvalidDifficultyError as e:
            raise HTTPException(status_code=400, detail=f"Invalid difficulty: {e}")
        except Exception as e:
            logger.error(f"Error while creating wordset: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Error while creating wordset")

    def get_wordset(self, wordset_id: int) -> WordsetRead:
        try:
            wordset = self.wordset_repository.get_by_id(wordset_id)
            if wordset is None:
                raise WordsetNotFoundError(f"Wordset with id '{wordset_id}' was not found.")
            return wordset
        except WordsetNotFoundError as e:
            raise HTTPException(status_code=404, detail=f"Wordset with id '{wordset_id}' was not found.")
        except Exception as e:
            logger.error(f"Error while getting wordset: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error while getting wordset: {e}")

    def get_all_wordsets(self) -> list[WordsetRead]:
        try:
            return self.wordset_repository.get_all()
        except Exception as e:
            logger.error(f"Error while getting all wordsets: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error while getting all wordsets: {e}")

    def delete_wordset(self, wordset_id: int) -> None:
        try:
            deleted = self.wordset_repository.delete(wordset_id)
            if not deleted:
                raise WordsetNotFoundError(f"Wordset with id '{wordset_id}' was not found.")
        except WordsetNotFoundError as e:
            raise HTTPException(status_code=404, detail=f"Wordset with id '{wordset_id}' was not found.")
        except Exception as e:
            logger.error(f"Error while deleting wordset: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error while deleting wordset: {e}")

    def _ensure_valid_difficulty(self, difficulty_id: int) -> None:
        if not self.wordset_repository.difficulty_exists(difficulty_id):
            raise InvalidDifficultyError(f"Difficulty with id '{difficulty_id}' was not found.")

    def update_wordset(self, wordset_id, wordset_update: WordsetWrite) -> WordsetRead:
        try:
            self._ensure_valid_difficulty(wordset_update.difficulty)
            return self.wordset_repository.update(wordset_id, wordset_update)
        except InvalidDifficultyError as e:
            raise HTTPException(status_code=400, detail=f"Invalid difficulty: {e}")
        except Exception as e:
            logger.error(f"Error while updating wordset: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error while updating wordset: {e}")
