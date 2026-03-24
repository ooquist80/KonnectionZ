import datetime

from pydantic import BaseModel
from app.models.wordset import Wordset


class Game(BaseModel):
    id: int | None = None
    user_id: int
    gameset_id: int
    start_time: datetime.datetime | None = None
    end_time: datetime.datetime | None = None
    wordsets: list[Wordset] = []