from fastapi import APIRouter, Depends, HTTPException, status, Security
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.api.deps import get_database_client, get_current_user
from app.db.client import DatabaseClient
from app.models.game import GameRead, GameNotFoundError
from app.models.gameset import GameSetNotFoundError
from app.services.game_service import GameService

router = APIRouter(prefix="/games", tags=["games"], dependencies=[Security(get_current_user, scopes=["user:admin"])])


def get_game_service(database_client: DatabaseClient = Depends(get_database_client)) -> GameService:
    return GameService(database_client)


@router.get("/{game_id}", status_code=status.HTTP_200_OK)
def get_game(game_id: int,
             game_service: GameService = Depends(get_game_service)
             ) -> GameRead:
    try:
        return game_service.get_game(game_id)
    except GameNotFoundError as exception:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(exception)) from exception
    except GameSetNotFoundError as exception:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(exception)) from exception


@router.get("/", status_code=status.HTTP_200_OK)
def get_games(game_service: GameService = Depends(get_game_service)) -> list[GameRead]:
    return game_service.get_games()
