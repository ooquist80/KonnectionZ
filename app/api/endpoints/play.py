from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.db.client import DatabaseClient
from app.models.play import GameStatus
from app.api.deps import get_database_client, get_current_user
from app.models.user import UserRead
from app.services.play_service import PlayService

router = APIRouter(prefix="/play", tags=["play"])

def get_play_service(database_client: DatabaseClient = Depends(get_database_client)) -> PlayService:
    return PlayService(database_client)

@router.post("{gameset_id}", status_code=status.HTTP_201_CREATED)
def create_game(gameset_id: int,
                current_user: Annotated[UserRead, Depends(get_current_user)],
                play_service: PlayService = Depends(get_play_service)
                ) -> GameStatus:
    game = play_service.create_game(gameset_id, current_user.id)

