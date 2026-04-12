from datetime import datetime

from pydantic import BaseModel

class CommentRead(BaseModel):
    id: int
    announcement_id: int
    user_name: str
    commented_at: datetime
    content: str

class CommentWrite(BaseModel):
    announcement_id: int
    content: str