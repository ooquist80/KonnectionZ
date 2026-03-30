from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.status import HTTP_404_NOT_FOUND

from app.api.deps import get_database_client
from app.db.client import DatabaseClient
from app.models.user import UserRead, UserWrite, UserNotFoundError
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def get_user_service(database_client: DatabaseClient = Depends(get_database_client)) -> UserService:
    return UserService(database_client)

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                     user_service: Annotated[UserService, Depends(get_user_service)]) -> UserRead:
    user = decode_token(token, user_service)
    return user


def decode_token(token: str, user_service: UserService) -> UserRead:
    if token == "lol":
        user = user_service.get_user_by_id(1)
        return user
    else:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,)

@router.get("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
def get_me(current_user: Annotated[UserRead, Depends(get_current_user)]) -> UserRead:
    return current_user

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserWrite, user_service: UserService = Depends(get_user_service)) -> UserRead:
    return user_service.create_user(payload)


@router.get("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
def get_user(user_id: int, user_service: UserService = Depends(get_user_service)) -> UserRead:
    try:
        return user_service.get_user_by_id(user_id)
    except UserNotFoundError as exception:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(exception)) from exception

@router.post("/token")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
          user_service: UserService = Depends(get_user_service)):
    token = user_service.login(form_data.username, form_data.password)
    return token



