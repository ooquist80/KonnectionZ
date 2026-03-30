from typing import Annotated
from pydantic import Field
from fastapi import APIRouter, Depends, HTTPException, status
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from app.db.client import DatabaseClient
from app.models.game import GameRead, GameWrite, GameNotFoundError, PlayResult, ResultMessage, GameAlreadyCompletedError
from app.models.user import UserNotFoundError, UserRead
from app.models.gameset import GameSetNotFoundError
from app.services.game import GameService

from app.api.deps import get_database_client, get_current_user

router = APIRouter(prefix="/games", tags=["games"])


def get_game_service(database_client: DatabaseClient = Depends(get_database_client)) -> GameService:
    return GameService(database_client)


@router.post("/", response_model=GameRead, status_code=status.HTTP_201_CREATED)
def create_game(payload: GameWrite,
                current_user: Annotated[UserRead, Depends(get_current_user)],
                game_service: GameService = Depends(get_game_service)) -> GameRead:

    try:
        return game_service.create_game(current_user, payload)
    except UserNotFoundError as exception:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(exception)) from exception
    except GameSetNotFoundError as exception:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(exception)) from exception
    except Exception as exception:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exception)) from exception


@router.get("/{game_id}", response_model=GameRead, status_code=status.HTTP_200_OK)
def get_game(game_id: int,
             current_user: Annotated[UserRead, Depends(get_current_user)],
             game_service: GameService = Depends(get_game_service)
             ) -> GameRead:
    try:
        return game_service.get_game(game_id)
    except GameNotFoundError as exception:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(exception)) from exception

@router.get("/", response_model=list[GameRead], status_code=status.HTTP_200_OK)
def get_games(current_user: Annotated[UserRead, Depends(get_current_user)],
        game_service: GameService = Depends(get_game_service)) -> list[GameRead]:
    return game_service.get_games()

@router.put("/play/{game_id}", response_model=PlayResult, status_code=status.HTTP_200_OK)
def play_words(game_id: int,
               payload: list[str],
               current_user: Annotated[UserRead, Depends(get_current_user)],
               game_service: GameService = Depends(get_game_service)
               ) -> PlayResult:
    try:
        game = game_service.get_game(game_id)
    except GameNotFoundError as exception:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(exception)) from exception
    if current_user.id != game.user_id:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Game with id: {game_id} does not belong to user with id: {current_user.id}.") from None
    try:
        result_message = game_service.play_words(game, payload)
    except GameAlreadyCompletedError as exception:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(exception)) from exception

    if result_message == ResultMessage.CORRECT or result_message == ResultMessage.COMPLETED:
        game = game_service.get_game(game_id)
        return PlayResult(game=game, result_message=result_message)
    else:
        return PlayResult(game=game, result_message=result_message)


