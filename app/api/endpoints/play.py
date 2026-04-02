from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.db.client import DatabaseClient
from app.models.game import GameBelongsToAnotherUserError
from app.models.play import GameStatus, PlayResult, GameAlreadyCompletedError
from app.api.deps import get_database_client, get_current_user
from app.models.user import UserRead
from app.services.play_service import PlayService

router = APIRouter(prefix="/play", tags=["play"])

def get_play_service(database_client: DatabaseClient = Depends(get_database_client)) -> PlayService:
    return PlayService(database_client)

@router.post("/{gameset_id}", status_code=status.HTTP_201_CREATED)
def create_game(gameset_id: int,
                current_user: Annotated[UserRead, Depends(get_current_user)],
                play_service: PlayService = Depends(get_play_service)
                ) -> PlayResult:
    play_result = play_service.start_game(gameset_id, current_user.id)
    return play_result

@router.put("/{game_id}", status_code=status.HTTP_202_ACCEPTED)
def play_words(game_id: int,
               played_words: list[str],
               current_user: Annotated[UserRead, Depends(get_current_user)],
               play_service: PlayService = Depends(get_play_service)) -> PlayResult:
    try:
        play_result = play_service.play_words(game_id, current_user.id, played_words)
    except GameAlreadyCompletedError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    except GameBelongsToAnotherUserError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    return play_result

