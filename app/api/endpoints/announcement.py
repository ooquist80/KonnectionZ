from app.api.deps import get_database_client, get_current_user
from app.db.client import DatabaseClient
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.announcement import AnnouncementRead
from app.models.user import UserRead
from app.services.announcement_service import AnnouncementService

router = APIRouter(prefix="/announcements", tags=["announcements"])

def get_announcement_service(database_client: DatabaseClient = Depends(get_database_client)):
    return AnnouncementService(database_client)

@router.get("/")
def get_announcements(current_user: UserRead = Depends(get_current_user),
                      announcement_service: AnnouncementService = Depends(get_announcement_service)
                      ) -> list[AnnouncementRead]:
    return announcement_service.get_announcements()
