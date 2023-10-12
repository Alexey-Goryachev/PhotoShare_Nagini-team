from datetime import datetime
from typing import List
from enum import Enum
from pydantic import BaseModel

class Role(str, Enum):
    User = "User"
    Moderator = "Moderator"
    Administrator = "Administrator"

class UserModel(BaseModel):
    username: str
    email: str
    password: str
    roles: List[str] = ["User"]

class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    user: UserDb
    role: str
    detail: str = "User successfully created"

class TokenModel(BaseModel):
    access_token: str
    token_type: str = "bearer"
    message: str
