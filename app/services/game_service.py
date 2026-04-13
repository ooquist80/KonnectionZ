import logging
from datetime import datetime

from fastapi import HTTPException

from app.db.client import DatabaseClient
from app.models.game import GameRead, GameNotFoundError, GameWrite
from app.models.gameset import GameSetNotFoundError, GameSetRead
from app.models.user import UserNotFoundError, UserRead
from app.repositories.game_repository import GameRepository
from app.repositories.gameset_repository import GameSetRepository
from app.repositories.user_repository import UserRepository
from app.repositories.wordset_repository import WordsetRepository

logger = logging.getLogger(__name__)

class GameService:

    def __init__(self, database_client: DatabaseClient) -> None:
        self.game_repository = GameRepository(database_client)
        self.user_repository = UserRepository(database_client)
        self.gameset_repository = GameSetRepository(database_client)
        self.wordset_repository = WordsetRepository(database_client)

    def create_game(self, user: UserRead, game_write : GameWrite) -> GameRead:
        try:
            gameset = self.gameset_repository.get_by_id(game_write.gameset_id)
        except Exception as e:
            logger.error(f"Error fetching gameset before creating game: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error while creating game: {e}")

        if gameset is None:
            raise HTTPException(status_code=404, detail=f"Game with id: {game_write.gameset_id} was not found.")
        try:
            created_game = self.game_repository.create(user.id, game_write, gameset)
        except Exception as e:
            logger.error(f"Error while creating game: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error while creating game: {e}")
        return created_game

    def get_game(self, game_id: int) -> GameRead:
        try:
            game = self.game_repository.get_by_id(game_id)
        except Exception as e:
            logger.error(f"Error fetching game: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error while fetching game: {e}")
        if game is None:
            raise HTTPException(status_code=404, detail="Game with id: {game_id} was not found.")
        return game

    def get_games(self):
        try:
            games = self.game_repository.get_all()
        except Exception as e:
            logger.error(f"Error fetching games: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error while fetching games: {e}")
        return games

