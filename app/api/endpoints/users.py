from fastapi import APIRouter, Depends, HTTPException, status
from starlette.status import HTTP_404_NOT_FOUND

from app.api.deps import get_user_service
from app.models.user import User, UserNotFoundError
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(payload: User, user_service: UserService = Depends(get_user_service)) -> User:
    return user_service.create_user(payload)

@router.get("/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
def get_user(user_id: int, user_service: UserService = Depends(get_user_service)) -> User:
    try:
        return user_service.get_user(user_id)
    except UserNotFoundError as exception:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(exception)) from exception