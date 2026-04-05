from typing import List

from pydantic import BaseModel, EmailStr


class UserNotFoundError(Exception):
    pass


class UserRead(BaseModel):
    id: int
    email: str
    username: str
    avatar: str
    scopes: List[str]

class UserWrite(BaseModel):
    email: EmailStr
    username: str
    password: str
    scopes: str = "user:play"

class UserRecord(BaseModel):
    id: int
    email: str
    username: str
    password: str
    avatar: str
    scopes: List[str]
