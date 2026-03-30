import datetime
from enum import Enum

from pydantic import BaseModel
from app.models.wordset import WordsetRead


class GameNotFoundError(Exception):
    pass

class GameAlreadyCompletedError(Exception):
    pass

class GameRead(BaseModel):
    id: int | None = None
    user_id: int
    gameset_id: int
    start_time: datetime.datetime | None = None
    end_time: datetime.datetime | None = None
    completed_wordsets: list[WordsetRead] | None = None

class GameWrite(BaseModel):
    gameset_id: int

class GameRecord(BaseModel):
    id: int
    user_id: int
    gameset_id: int
    start_time: datetime.datetime
    end_time: datetime.datetime | None = None
    completed_wordset_ids: list[int]

class ResultMessage(str, Enum):
    COMPLETED = "Congratulations! You have completed the game."
    CORRECT = "Correct!"
    ALMOST_CORRECT = "Almost! Only one word is not correct."
    INCORRECT = "Incorrect! Try again."

class PlayResult(BaseModel):
    game: GameRead
    result_message: ResultMessage
