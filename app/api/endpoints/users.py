from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND

from app.api.deps import get_database_client, get_current_user
from app.db.client import DatabaseClient
from app.models.user import UserRead, UserWrite, UserNotFoundError
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(database_client: DatabaseClient = Depends(get_database_client)) -> UserService:
    return UserService(database_client)


@router.get("/me", status_code=status.HTTP_200_OK)
def get_me(current_user: Annotated[UserRead, Depends(get_current_user)]) -> UserRead:
    return current_user


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(payload: UserWrite,
                user_service: UserService = Depends(get_user_service)) -> UserRead | None:
    return user_service.create(payload)

@router.get("/")
def get_all_users(user_service: UserService = Depends(get_user_service),
                  current_user: UserRead = Security(get_current_user, scopes = ["user:admin"])) -> list[UserRead]:
    return user_service.get_all()

@router.get("/{user_id}")
def get_user(user_id: int,
             user_service: UserService = Depends(get_user_service),
             current_user: UserRead = Security(get_current_user, scopes = ["user:admin"])) -> UserRead:
    try:
        return user_service.get_by_id(user_id)
    except UserNotFoundError as exception:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(exception)) from exception

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int,
                user_service: UserService = Depends(get_user_service),
                current_user: UserRead = Security(get_current_user, scopes = ["user:admin"])) -> JSONResponse:
    try:
        user_service.delete(user_id)
    except UserNotFoundError as exception:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(exception)) from exception

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={"detail": f"User with id {user_id} was deleted."})