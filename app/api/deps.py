from fastapi import Depends

from app.core.config import Settings, get_settings
from app.db.client import DatabaseClient
from app.repositories.game import GameRepository
from app.repositories.wordset import WordsetRepository
from app.services.game import GameService
from app.services.wordset import WordsetService


def get_database_client(settings: Settings = Depends(get_settings)) -> DatabaseClient:
    return DatabaseClient(settings)

def get_wordset_repository(
    database_client: DatabaseClient = Depends(get_database_client),
) -> WordsetRepository:
    return WordsetRepository(database_client)

def get_wordset_service(
    wordset_repository: WordsetRepository = Depends(get_wordset_repository),
) -> WordsetService:
    return WordsetService(wordset_repository)

def get_game_repository(database_client: DatabaseClient = Depends(get_database_client)) -> GameRepository:
    return GameRepository(database_client)

def get_game_service(game_repository: GameRepository = Depends(get_game_repository)) -> GameService:
    return GameService(game_repository)
