from app.repositories.game import GameRepository
from app.models.game import Game, GameNotFoundError
from app.db.client import DatabaseClient
from datetime import datetime


class GameService:

    def __init__(self, database_client: DatabaseClient) -> None:
        self.game_repository = GameRepository(database_client)

    def create_game(self, payload) -> Game:
        start_time = datetime.now()
        created_game = self.game_repository.create(user_id=payload.user_id, gameset_id=payload.gameset_id,
                                                   start_time=start_time)
        return created_game

    def get_game(self, game_id: int) -> Game:
        game = self.game_repository.get_by_id(game_id)
        if game is None:
            raise GameNotFoundError(f"Game with id: {game_id} was not found.")
        return game

    def play_words(self, game_id, payload):
        pass
