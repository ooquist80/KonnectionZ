import logging

from fastapi import HTTPException

from app.db.client import DatabaseClient
from app.models.announcement import AnnouncementRead
from app.repositories.announcement_repository import AnnouncementRepository

logger = logging.getLogger(__name__)

class AnnouncementService:
    def __init__(self, database_client: DatabaseClient ):
        self.announcement_repository = AnnouncementRepository(database_client)

    def get_announcements(self) -> list[AnnouncementRead]:
        try:
            return self.announcement_repository.get_all_announcements()
        except Exception as e:
            logger.error(f"Error getting announcements: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error fetching announcements: {e}")