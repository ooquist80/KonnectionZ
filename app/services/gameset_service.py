from typing import List

from app.models.wordset import WordsetRead
from app.repositories.gameset_repository import GameSetRepository
from app.repositories.wordset_repository import WordsetRepository
from app.models.gameset import GameSetRead, GameSetWrite, GameSetNotFoundError
from app.db.client import DatabaseClient


class GameSetService:

    def __init__(self, database_client: DatabaseClient) -> None:
        self.gameset_repository = GameSetRepository(database_client)
        self.wordset_repository = WordsetRepository(database_client)

    def create_gameset(self, gameset: GameSetWrite) -> GameSetRead:
        created_gameset = self.gameset_repository.create(name=gameset.name, date=gameset.date, daily=gameset.daily,
                                                         wordset_ids=gameset.wordsets)
        return created_gameset

    def get_gameset(self, gameset_id: int) -> GameSetRead:
        gameset = self.gameset_repository.get_by_id(gameset_id)
        if gameset is None:
            raise GameSetNotFoundError(f"Gameset with id: {gameset_id} was not found.")

        return gameset

    def get_all_gamesets(self) -> List[GameSetRead]:
        gamesets = self.gameset_repository.get_all()
        return gamesets

    def delete_gameset(self, gameset_id: int) -> None:
        self.gameset_repository.delete(gameset_id)
