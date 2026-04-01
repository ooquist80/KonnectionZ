from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_database_client
from app.db.client import DatabaseClient
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

def get_auth_service(database_client: DatabaseClient = Depends(get_database_client)) -> AuthService:
    return AuthService(database_client)

@router.post("/token")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
          auth_service: AuthService = Depends(get_auth_service)):
    token = auth_service.login(form_data.username, form_data.password, form_data.scopes)
    return token