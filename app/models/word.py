from pydantic import BaseModel

class WordIndDB(BaseModel):
    id: int
    word: str
    wordset_id: int

class WordRead(BaseModel):
    id: int
    word: str
