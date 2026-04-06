from datetime import datetime

from pydantic import BaseModel

class AnnouncementRead(BaseModel):
    id: int
    user_id: int | None
    announced_at: datetime
    content: str

class AnnouncementWrite(BaseModel):
    user_id: int
    content: str