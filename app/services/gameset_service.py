import logging
from typing import List

from fastapi import HTTPException

from app.db.client import DatabaseClient
from app.models.gameset import GameSetRead, GameSetWrite, GameSetNotFoundError
from app.repositories.gameset_repository import GameSetRepository
from app.repositories.wordset_repository import WordsetRepository

logger = logging.getLogger(__name__)

class GameSetService:

    def __init__(self, database_client: DatabaseClient) -> None:
        self.gameset_repository = GameSetRepository(database_client)
        self.wordset_repository = WordsetRepository(database_client)

    def create_gameset(self, gameset: GameSetWrite) -> GameSetRead:
        try:
            created_gameset = self.gameset_repository.create(name=gameset.name,
                                                             date=gameset.date,
                                                             daily_date=gameset.daily_date,
                                                             wordset_ids=gameset.wordsets)
        except Exception as e:
            logger.error(f"Error while creating gameset: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error while creating gameset: {e}")
        return created_gameset

    def get_gameset(self, gameset_id: int) -> GameSetRead:
        try:
            gameset = self.gameset_repository.get_by_id(gameset_id)
        except Exception as e:
            logger.error(f"Error while getting gameset: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error while getting gameset: {e}")
        if gameset is None:
            raise HTTPException(status_code=404, detail=f"Gameset with id: {gameset_id} was not found.")
        return gameset

    def get_all_gamesets(self) -> List[GameSetRead]:
        try:
            gamesets = self.gameset_repository.get_all()
        except Exception as e:
            logger.error(f"Error while getting gamesets: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error while getting gamesets: {e}")
        return gamesets

    def delete_gameset(self, gameset_id: int) -> None:
        try:
            self.gameset_repository.delete(gameset_id)
        except Exception as e:
            logger.error(f"Error while deleting gameset: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error while deleting gameset: {e}")
