from pydantic import BaseModel, EmailStr


class UserNotFoundError(Exception):
    pass


class UserRead(BaseModel):
    id: int
    email: str
    username: str

class UserWrite(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserRecord(BaseModel):
    id: int
    email: str
    username: str
    password: str
