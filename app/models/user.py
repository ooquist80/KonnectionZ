from pydantic import BaseModel


class UserNotFoundError(Exception):
    pass


class User(BaseModel):
    id: int | None = None
    email: str
    username: str
    password: str | None = None
