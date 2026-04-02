from pydantic import BaseModel, Field

from app.models.word import WordRead


class WordsetRegisteredInGameError(Exception):
    pass


class WordsetNotFoundError(Exception):
    pass


class WordsetInDB(BaseModel):
    id: int
    category: str
    difficulty: int


class WordsetRead(BaseModel):
    id: int | None = None
    category: str
    difficulty: int
    words: list[WordRead] = Field(min_length=4)
