from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from app.models.wordset import WordsetRead

class GameAlreadyCompletedError(Exception):
    pass

class GameStatus(BaseModel):
    game_name: str
    start_time: datetime
    end_time: datetime | None = None
    words_remaining: list[str]
    wordsets_completed: list[WordsetRead]
    turn_count: int = 0

class ResultMessage(str, Enum):
    COMPLETED = "Congratulations! You have completed the game."
    CORRECT = "Correct!"
    ALMOST_CORRECT = "Almost! Only one word is not correct."
    INCORRECT = "Incorrect! Try again."

class PlayResult(BaseModel):
    game_id: int
    game_status: GameStatus
    result_message: ResultMessage | None = None

class PlayGameSet(BaseModel):
    id: int
    name: str
    daily: bool
    turn_count: int | None
    start_time: datetime | None
    end_time: datetime | None


