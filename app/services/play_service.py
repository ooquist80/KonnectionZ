from app.db.client import DatabaseClient
from app.repositories.game_repository import GameRepository


class PlayService:
    def __init__(self, database_client: DatabaseClient):
        self.game_repository = GameRepository(database_client)

    def create_game(self, gameset_id, user_id):
        self.game_repository.create(gameset_id, user_id)