from fastapi import APIRouter, Depends, HTTPException, status
from starlette.status import HTTP_404_NOT_FOUND

from app.db.client import DatabaseClient
from app.models.game import Game, GameNotFoundError
from app.services.game import GameService
from app.api.deps import get_database_client

router = APIRouter(prefix="/games", tags=["games"])


def get_game_service(database_client: DatabaseClient = Depends(get_database_client)) -> GameService:
    return GameService(database_client)


@router.post("/", response_model=Game, status_code=status.HTTP_201_CREATED)
def create_game(payload: Game, game_service: GameService = Depends(get_game_service)) -> Game:
    return game_service.create_game(payload)


@router.get("/{game_id}", response_model=Game, status_code=status.HTTP_200_OK)
def get_game(game_id: int, game_service: GameService = Depends(get_game_service)) -> Game:
    try:
        return game_service.get_game(game_id)
    except GameNotFoundError as exception:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(exception)) from exception


@router.post("/{game_id}/play", response_model=Game, status_code=status.HTTP_200_OK)
def play_words(game_id: int, payload: list[str], game_service: GameService = Depends(get_game_service)):
    try:
        game = game_service.get_game(game_id)
    except GameNotFoundError as exception:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(exception)) from exception
    game_service.play_words(game_id, payload)
