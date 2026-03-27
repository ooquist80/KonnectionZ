import datetime
from pydantic import BaseModel, Field


class GameSetNotFoundError(Exception):
    pass


class GameSetRead(BaseModel):
    id: int | None = None
    date: datetime.datetime
    name: str = Field(title="The name of the game")
    wordsets: list[int] = Field(min_length=4)

class GameSetWrite(BaseModel):
    date: datetime.datetime = datetime.datetime.now()
    name: str = Field(title="The name of the game")
    wordsets: list[int] = Field(min_length=4)
