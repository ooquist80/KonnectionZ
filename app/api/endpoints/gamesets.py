from fastapi import APIRouter, Depends, HTTPException, status
from starlette.status import HTTP_404_NOT_FOUND

from app.api.deps import get_database_client
from app.db.client import DatabaseClient
from app.models.gameset import GameSet
from app.services.gameset import GameSetService, GameSetNotFoundError

router = APIRouter(prefix="/gamesets", tags=["gamesets"])

def get_gameset_service(database_client: DatabaseClient = Depends(get_database_client)) -> GameSetService:
    return GameSetService(database_client)

@router.post("/", response_model=GameSet, status_code=status.HTTP_201_CREATED)
def create_gameset(payload: GameSet, gameset_service: GameSetService = Depends(get_gameset_service)) -> GameSet:
    return gameset_service.create_gameset(payload)

@router.get("/{gameset_id}", response_model=GameSet, status_code=status.HTTP_200_OK)
def get_gameset(gameset_id: int, gameset_service: GameSetService = Depends(get_gameset_service)) -> GameSet:
    try:
        return gameset_service.get_gameset(gameset_id)
    except GameSetNotFoundError as exception:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(exception)) from exception