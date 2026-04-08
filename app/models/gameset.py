import datetime
from pydantic import BaseModel, Field
from app.models.wordset import WordsetRead


class GameSetNotFoundError(Exception):
    pass

class GameSetRead(BaseModel):
    id: int
    date: datetime.datetime
    daily_date: datetime.datetime | None
    name: str = Field(title="The name of the game")
    wordsets: list[WordsetRead] = Field(min_length=4)

class GameSetWrite(BaseModel):
    date: datetime.datetime = datetime.datetime.now()
    daily_date: datetime.datetime | None = None
    name: str = Field(title="The name of the game")
    wordsets: list[int] = Field(min_length=4)
