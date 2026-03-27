import datetime
from enum import Enum

from pydantic import BaseModel
from app.models.wordset import WordsetRead


class GameNotFoundError(Exception):
    pass


class GameRead(BaseModel):
    id: int | None = None
    user_id: int
    gameset_id: int
    start_time: datetime.datetime | None = None
    end_time: datetime.datetime | None = None
    completed_wordsets: list[WordsetRead] | None = None

class GameWrite(BaseModel):
    user_id: int
    gameset_id: int
    start_time: datetime.datetime | None = None
    end_time: datetime.datetime | None = None

class GameRecord(BaseModel):
    id: int
    user_id: int
    gameset_id: int
    start_time: datetime.datetime
    end_time: datetime.datetime | None = None
    completed_wordset_ids: list[int]

class Resultmessage(str, Enum):
    COMPLETED = "Congratulations! You have completed the game."
    CORRECT = "Correct!"
    THREE_CORRECT = "Almost! Three out of four words are correct."
    INCORRECT = "Incorrect! Try again."

class PlayResult(BaseModel):
    game: GameRead
    result: Resultmessage
