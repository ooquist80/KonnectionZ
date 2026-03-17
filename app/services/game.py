from app.repositories.game import GameRepository
from app.models.game import Game

class GameNotFoundError(Exception):
    pass

class GameService:

    def __init__(self, game_repository: GameRepository) -> None:
        self.game_repository = game_repository

    def create_game(self, payload: Game) -> Game:
        created_game = self.game_repository.create(name=payload.name, date=payload.date, wordsets=payload.wordsets )
        return created_game

    def get_game(self, game_id: int) -> Game:
        game = self.game_repository.get_by_id(game_id)
        if game is None:
            raise GameNotFoundError(f"Game with id: {game_id} was not found.")
        return game

    def delete_game(self, game_id: int) -> None:
        self.game_repository.delete(game_id)
