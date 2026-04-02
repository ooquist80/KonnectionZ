from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status, Security

from app.api.deps import get_database_client, get_current_user
from app.db.client import DatabaseClient
from app.models.user import UserRead
from app.models.wordset import WordsetRead, WordsetNotFoundError, WordsetRegisteredInGameError, WordsetWrite
from app.services.wordset_service import InvalidDifficultyError, WordsetService

router = APIRouter(prefix="/wordsets", tags=["wordsets"], dependencies=[Security(get_current_user, scopes = ["user:admin"])])


def get_wordset_service(database_client: DatabaseClient = Depends(get_database_client)) -> WordsetService:
    return WordsetService(database_client)


@router.post("", response_model=WordsetRead, status_code=status.HTTP_201_CREATED)
def create_wordset(
        payload: WordsetWrite,
        wordset_service: WordsetService = Depends(get_wordset_service)) -> WordsetRead:
    try:
        return wordset_service.create_wordset(payload)
    except InvalidDifficultyError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("", response_model=list[WordsetRead])
def list_wordsets(wordset_service: WordsetService = Depends(get_wordset_service)) -> list[WordsetRead]:
    return wordset_service.get_all_wordsets()


@router.get("/{wordset_id}", response_model=WordsetRead)
def get_wordset(
        wordset_id: int,
        wordset_service: WordsetService = Depends(get_wordset_service),
        ) -> WordsetRead:
    try:
        return wordset_service.get_wordset(wordset_id)
    except WordsetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/{wordset_id}", response_model=WordsetRead)
def update_wordset(
        wordset_id: int,
        payload: WordsetWrite,
        wordset_service: WordsetService = Depends(get_wordset_service),
        ) -> WordsetRead:
    try:
        return wordset_service.update_wordset(wordset_id, payload)
    except InvalidDifficultyError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except WordsetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{wordset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wordset(
        wordset_id: int,
        wordset_service: WordsetService = Depends(get_wordset_service),
        ) -> Response:
    try:
        wordset_service.delete_wordset(wordset_id)
    except WordsetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except WordsetRegisteredInGameError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
