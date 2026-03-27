from app.repositories.gameset import GameSetRepository
from app.models.gameset import GameSetRead, GameSetWrite, GameSetNotFoundError
from app.db.client import DatabaseClient


class GameSetService:

    def __init__(self, database_client: DatabaseClient) -> None:
        self.gameset_repository = GameSetRepository(database_client)

    def create_gameset(self, payload: GameSetWrite) -> GameSetRead:
        created_gameset = self.gameset_repository.create(name=payload.name, date=payload.date,
                                                         wordsets=payload.wordsets)
        return created_gameset

    def get_gameset(self, gameset_id: int) -> GameSetRead:
        gameset = self.gameset_repository.get_by_id(gameset_id)
        if gameset is None:
            raise GameSetNotFoundError(f"Gameset with id: {gameset_id} was not found.")
        return gameset

    def delete_gameset(self, gameset_id: int) -> None:
        self.gameset_repository.delete(gameset_id)
