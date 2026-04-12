from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_database_client, get_current_user
from app.db.client import DatabaseClient
from app.models.comment import CommentRead, CommentWrite
from app.models.user import UserRead
from app.services.comment_service import CommentService

router = APIRouter(prefix="/comments", tags=["comments"])

def get_comments_service(database_client: DatabaseClient = Depends(get_database_client)):
    return CommentService(database_client)

@router.get("/{announcement_id}")
def get_comments_by_announcement_id(announcement_id: int,
                                    comments_service: CommentService = Depends(get_comments_service)) -> list[CommentRead]:
    return comments_service.get_comments_by_announcement_id(announcement_id)

@router.post("/", status_code=201)
def create_comment(current_user: Annotated[UserRead, Depends(get_current_user)],
                   comment_write: CommentWrite,
                   comments_service: CommentService = Depends(get_comments_service)) -> CommentRead:
    return comments_service.create_comment(current_user, comment_write)