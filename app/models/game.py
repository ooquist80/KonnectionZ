import datetime

from pydantic import BaseModel


class GameNotFoundError(Exception):
    pass


class Game(BaseModel):
    id: int | None = None
    user_id: int
    gameset_id: int
    start_time: datetime.datetime | None = None
    end_time: datetime.datetime | None = None
    completed_wordsets: list[int] | None = None
