from app.repositories.gameset import GameSetRepository
from app.models.gameset import GameSet, GameSetNotFoundError


class GameSetService:

    def __init__(self, game_repository: GameSetRepository) -> None:
        self.game_repository = game_repository

    def create_gameset(self, payload: GameSet) -> GameSet:
        created_gameset = self.game_repository.create(name=payload.name, date=payload.date, wordsets=payload.wordsets )
        return created_gameset

    def get_gameset(self, gameset_id: int) -> GameSet:
        gameset = self.game_repository.get_by_id(gameset_id)
        if gameset is None:
            raise GameSetNotFoundError(f"Game with id: {gameset_id} was not found.")
        return gameset

    def delete_gameset(self, gameset_id: int) -> None:
        self.game_repository.delete(gameset_id)
