from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from app.models.wordset import WordsetRead

class GameStatus(BaseModel):
    start_date: datetime
    end_date: datetime | None = None
    words_left: list[str]
    wordsets_completed: list[WordsetRead]
    turn_count: int = 0

class ResultMessage(str, Enum):
    COMPLETED = "Congratulations! You have completed the game."
    CORRECT = "Correct!"
    ALMOST_CORRECT = "Almost! Only one word is not correct."
    INCORRECT = "Incorrect! Try again."

class PlayResult(BaseModel):
    game_status: GameStatus
    result_message: ResultMessage


