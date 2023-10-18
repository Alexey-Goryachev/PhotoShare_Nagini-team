from datetime import datetime
from typing import List
from enum import Enum
from fastapi import UploadFile
from pydantic import BaseModel, EmailStr, constr, SecretStr


class Role(str, Enum):
    User = "User"
    Moderator = "Moderator"
    Administrator = "Administrator"


class UserModel(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_active: bool
    roles: List[str] = ["User"]


class UserDb(BaseModel):
    id: int
    username: str
    email: EmailStr
    photos: List
    created_at: datetime

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    role: str
    detail: str = "User successfully created"

class UserUpdate(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    password: SecretStr



class TokenModel(BaseModel):
    access_token: str
    token_type: str = "bearer"
    message: str


class PhotoBase(BaseModel):
    image_url: str
    description: str


class PhotoCreate(BaseModel):
    description: str


class PhotoUpdate(BaseModel):
    description: str


class PhotoResponse(BaseModel):
    id: int
    image_url: str
    description: str
    created_at: datetime


class PhotoListResponse(BaseModel):
    photos: List[PhotoResponse]
