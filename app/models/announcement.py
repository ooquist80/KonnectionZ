from datetime import datetime

from pydantic import BaseModel

class AnnouncementRead(BaseModel):
    id: int
    user_id: int | None
    announced_at: datetime
    content: str
    comment_count: int = 0

class AnnouncementWrite(BaseModel):
    user_id: int
    content: str