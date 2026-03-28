from pydantic import BaseModel, EmailStr


class UserNotFoundError(Exception):
    pass


class UserRead(BaseModel):
    id: int
    email: str
    password: str
    username: str

class UserWrite(BaseModel):
    email: EmailStr
    username: str
    password: str
