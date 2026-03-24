from fastapi import APIRouter, Depends, HTTPException, status
from starlette.status import HTTP_404_NOT_FOUND

from app.api.deps import get_game_service
from app.models.gameset import GameSet
from app.services.gameset import GameSetService, GameSetNotFoundError

router = APIRouter(prefix="/gamesets", tags=["gamesets"])

@router.post("/", response_model=GameSet, status_code=status.HTTP_201_CREATED)
def create_gameset(payload: GameSet, game_service: GameSetService = Depends(get_game_service)) -> GameSet:
    return game_service.create_gameset(payload)

@router.get("/{gameset_id}", response_model=GameSet, status_code=status.HTTP_200_OK)
def get_gameset(gameset_id: int, game_service: GameSetService = Depends(get_game_service)) -> GameSet:
    try:
        return game_service.get_gameset(gameset_id)
    except GameSetNotFoundError as exception:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(exception)) from exception