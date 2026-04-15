from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Security
from starlette.status import HTTP_404_NOT_FOUND

from app.api.deps import get_database_client, get_current_user
from app.db.client import DatabaseClient
from app.models.gameset import GameSetRead, GameSetWrite
from app.models.user import UserRead
from app.services.gameset_service import GameSetService, GameSetNotFoundError

router = APIRouter(prefix="/gamesets", tags=["gamesets"])


def get_gameset_service(database_client: DatabaseClient = Depends(get_database_client)) -> GameSetService:
    return GameSetService(database_client)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_gameset(payload: GameSetWrite,
                   gameset_service: GameSetService = Depends(get_gameset_service),
                   current_user: UserRead = Security(get_current_user, scopes=["user:gamemaster"])
                   ) -> GameSetRead:
    return gameset_service.create_gameset(payload)


@router.get("/{gameset_id}", status_code=status.HTTP_200_OK)
def get_gameset(gameset_id: int,
                gameset_service: GameSetService = Depends(get_gameset_service),
                current_user: UserRead = Security(get_current_user, scopes=["user:admin"])
                ) -> GameSetRead:
    try:
        return gameset_service.get_gameset(gameset_id)
    except GameSetNotFoundError as exception:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(exception)) from exception


@router.get("/")
def get_gamesets(gameset_service: GameSetService = Depends(get_gameset_service),
                 current_user: UserRead = Security(get_current_user, scopes=["user:admin"])
                 ) -> List[GameSetRead]:
    return gameset_service.get_all_gamesets()
