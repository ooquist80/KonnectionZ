import datetime
from pydantic import BaseModel, Field

class GameSetNotFoundError(Exception):
    pass

class GameSet(BaseModel):
    id: int | None = None
    date: datetime.datetime | None = datetime.datetime.now()
    name: str = Field(title="The name of the game")
    wordsets: list[int] = Field(min_length=4)
