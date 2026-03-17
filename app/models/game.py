import datetime
from pydantic import BaseModel, Field

class GameNotFoundError(Exception):
    pass

class Game(BaseModel):
    id: int | None = None
    date: datetime.datetime | None = datetime.datetime.now()
    name: str = Field(title="The name of the game")
    wordsets: list[int] = Field(min_length=4)
