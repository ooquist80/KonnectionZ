import logging

from fastapi import HTTPException

from app.db.client import DatabaseClient
from app.models.comment import CommentWrite, CommentRead
from app.models.user import UserRead
from app.repositories.comment_repository import CommentRepository

logger = logging.getLogger(__name__)

class CommentService:
    def __init__(self, database_client: DatabaseClient):
        self.comment_repository = CommentRepository(database_client)

    def get_comments_by_announcement_id(self, announcement_id: int) -> list[CommentRead]:
        try:
            return self.comment_repository.get_by_announcement_id(announcement_id)
        except Exception as e:
            logger.error(f"Error getting comments: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error getting comments: {e}")

    def create_comment(self, user : UserRead, comment_write: CommentWrite):
        try:
            return self.comment_repository.create_comment(user, comment_write)
        except Exception as e:
            logger.error(f"Error creating comment: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error creating comment: {e}")
