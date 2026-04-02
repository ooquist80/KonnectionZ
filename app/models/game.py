import datetime

from pydantic import BaseModel

from app.models.gameset import GameSetRead


class GameNotFoundError(Exception):
    pass

class GameBelongsToAnotherUserError(Exception):
    pass

class GameRead(BaseModel):
    id: int
    user_id: int
    gameset: GameSetRead
    start_time: datetime.datetime
    end_time: datetime.datetime | None = None
    completed_wordsets: list[int] = []

class GameWrite(BaseModel):
    gameset_id: int

