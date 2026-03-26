from fastapi import APIRouter, Depends, HTTPException, status
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from app.db.client import DatabaseClient
from app.models.game import GameRead, GameCreate, GameNotFoundError, PlayResult, Resultmessage
from app.models.user import UserNotFoundError
from app.models.gameset import GameSetNotFoundError
from app.services.game import GameService
from app.api.deps import get_database_client

router = APIRouter(prefix="/games", tags=["games"])


def get_game_service(database_client: DatabaseClient = Depends(get_database_client)) -> GameService:
    return GameService(database_client)


@router.post("/", response_model=GameRead, status_code=status.HTTP_201_CREATED)
def create_game(payload: GameCreate, game_service: GameService = Depends(get_game_service)) -> GameRead:
    try:
        return game_service.create_game(payload)
    except UserNotFoundError as exception:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(exception)) from exception
    except GameSetNotFoundError as exception:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(exception)) from exception
    except Exception as exception:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exception)) from exception


@router.get("/{game_id}", response_model=GameRead, status_code=status.HTTP_200_OK)
def get_game(game_id: int, game_service: GameService = Depends(get_game_service)) -> GameRead:
    try:
        return game_service.get_game(game_id)
    except GameNotFoundError as exception:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(exception)) from exception

@router.get("/", response_model=list[GameRead], status_code=status.HTTP_200_OK)
def get_games(game_service: GameService = Depends(get_game_service)) -> list[GameRead]:
    return game_service.get_games()

@router.put("/play/{game_id}", response_model=PlayResult, status_code=status.HTTP_200_OK)
def play_words(game_id: int, payload: list[str], game_service: GameService = Depends(get_game_service)):
    try:
        game = game_service.get_game(game_id)
    except GameNotFoundError as exception:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(exception)) from exception
    result = game_service.play_words(game, payload)

    if result == Resultmessage.CORRECT:
        game = game_service.get_game(game_id)
        return PlayResult(game=game, result=result)
    else:
        return PlayResult(game=game, result=result)


