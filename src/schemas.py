from datetime import datetime
from typing import List, Optional
from enum import Enum
from fastapi import UploadFile
from pydantic import BaseModel, EmailStr, Field
from typing import List
from enum import Enum
from fastapi import UploadFile
from pydantic import BaseModel, EmailStr


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


class PhotoBase(BaseModel):
    image_url: str
    description: str


class PhotoCreate(BaseModel):
    description: str
    #user_id: int 


class PhotoUpdate(BaseModel):
    description: str


class PhotoResponse(BaseModel):
    id: int
    image_url: str
    description: str
    created_at: datetime


class PhotoListResponse(BaseModel):
    photos: List[PhotoResponse]


# =======

class CommentBase(BaseModel):
    text: str = Field(max_length=500)


class CommentModel(CommentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # user_id: int
    photos_id: int
    update_status: bool = False

    class Config:
        orm_mode = True


class CommentUpdate(CommentModel):
    update_status: bool = True
    updated_at: datetime

    class Config:
        orm_mode = True


# ======

class TagBase(BaseModel):
    title: str = Field(max_length=50)


class TagModel(TagBase):
    pass

    class Config:
        orm_mode = True


class TagResponse(TagBase):
    id: int
    # user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
