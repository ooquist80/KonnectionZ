from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Security
from starlette.status import HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST

from app.api.deps import get_database_client, get_current_user
from app.db.client import DatabaseClient
from app.models.game import GameRead, GameNotFoundError, GameBelongsToAnotherUserError
from app.models.gameset import GameSetNotFoundError
from app.models.user import UserRead
from app.services.game_service import GameService

router = APIRouter(prefix="/games", tags=["games"], dependencies=[Security(get_current_user, scopes = ["user:admin"])])


def get_game_service(database_client: DatabaseClient = Depends(get_database_client)) -> GameService:
    return GameService(database_client)



@router.get("/{game_id}", response_model=GameRead, status_code=status.HTTP_200_OK)
def get_game(game_id: int,
             current_user: Annotated[UserRead, Depends(get_current_user)],
             game_service: GameService = Depends(get_game_service)
             ) -> GameRead:
    try:
        return game_service.get_game(game_id)
    except GameNotFoundError as exception:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(exception)) from exception
    except GameSetNotFoundError as exception:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(exception)) from exception

@router.get("/", response_model=list[GameRead], status_code=status.HTTP_200_OK)
def get_games(current_user: Annotated[UserRead, Depends(get_current_user)],
        game_service: GameService = Depends(get_game_service)) -> list[GameRead]:
    return game_service.get_games()



