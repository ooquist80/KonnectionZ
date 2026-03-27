from pydantic import BaseModel


class UserNotFoundError(Exception):
    pass


class UserRead(BaseModel):
    id: int
    email: str
    username: str

class UserWrite(BaseModel):
    email: str
    username: str
    password: str
