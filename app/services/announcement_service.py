from app.db.client import DatabaseClient
from app.models.announcement import AnnouncementRead
from app.repositories.announcement_repository import AnnouncementRepository


class AnnouncementService:
    def __init__(self, database_client: DatabaseClient ):
        self.announcement_repository = AnnouncementRepository(database_client)

    def get_announcements(self) -> list[AnnouncementRead]:
        return self.announcement_repository.get_all_announcements()