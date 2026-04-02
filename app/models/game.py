import datetime
from enum import Enum

from pydantic import BaseModel
from app.models.wordset import WordsetRead
from app.models.gameset import GameSetRead


class GameNotFoundError(Exception):
    pass

class GameAlreadyCompletedError(Exception):
    pass

class GameBelongsToAnotherUserError(Exception):
    pass

class GameRead(BaseModel):
    id: int | None = None
    user_id: int
    gameset: GameSetRead
    start_time: datetime.datetime | None = None
    end_time: datetime.datetime | None = None
    completed_wordsets: list[int] | None = None

class GameWrite(BaseModel):
    gameset_id: int

