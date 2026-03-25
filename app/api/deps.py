from fastapi import Depends

from app.core.config import Settings, get_settings
from app.db.client import DatabaseClient
from app.repositories.gameset import GameSetRepository
from app.repositories.wordset import WordsetRepository
from app.repositories.user import UserRepository
from app.repositories.game import GameRepository
from app.services.gameset import GameSetService
from app.services.wordset import WordsetService
from app.services.user import UserService
from app.services.game import GameService




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

def get_gameset_repository(database_client: DatabaseClient = Depends(get_database_client)) -> GameSetRepository:
    return GameSetRepository(database_client)

def get_gameset_service(gameset_repository: GameSetRepository = Depends(get_gameset_repository)) -> GameSetService:
    return GameSetService(gameset_repository)

def get_user_repository(database_client: DatabaseClient = Depends(get_database_client)) -> UserRepository:
    return UserRepository(database_client)

def get_user_service(user_repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repository)

def get_game_repository(database_client: DatabaseClient = Depends(get_database_client)) -> GameRepository:
    return GameRepository(database_client)


