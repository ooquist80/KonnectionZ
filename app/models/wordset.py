from pydantic import BaseModel, Field


class WordsetRegisteredInGameError(Exception):
    pass


class WordsetNotFoundError(Exception):
    pass


class WordsetRead(BaseModel):
    id: int | None = None
    category: str
    difficulty: int
    words: list[str] = Field(min_length=4)

class WordsetCreate(BaseModel):
    category: str
    difficulty: int
    words: list[str] = Field(min_length=4)

class WordsetUpdate(BaseModel):
    category: str
    difficulty: int
    words: list[str] = Field(min_length=4)
