from datetime import datetime
from typing import List
from enum import Enum
from fastapi import UploadFile
from pydantic import BaseModel, EmailStr, Field


class Role(str, Enum):
    User = "User"
    Moderator = "Moderator"
    Administrator = "Administrator"


class UserModel(BaseModel):
    username: str
    email: EmailStr
    password: str
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
    #TODO
    image_transform: str
    qr_transform: str
    public_id: str
########################

class PhotoCreate(BaseModel):
    description: str


class PhotoUpdate(BaseModel):
    description: str


class PhotoResponse(BaseModel):
    id: int
    image_url: str
    description: str
    created_at: datetime
    #TODO
    # updated_at: datetime
    # # user_id : int
    # image_transform: str
    # qr_transform: str
    # public_id: str

class PhotoListResponse(BaseModel):
    photos: List[PhotoResponse]



#Models for transformation photos
class PhotoTransform(BaseModel): 
    id: int
    image_transform: str
    # qr_transform: str
    detail: str = "Image successfully transform"

class PhotoLinkTransform(BaseModel):
    image_transform: str
    # qr_transform: str

class TransformCircleModel(BaseModel):
    use_filter: bool = False
    height: int = Field(ge=0, default=400)
    width: int = Field(ge=0, default=400)


class TransformEffectModel(BaseModel):
    use_filter: bool = False
    art_audrey: bool = False
    art_zorro: bool = False
    cartoonify: bool = False
    blur: bool = False
    

class TransformResizeModel(BaseModel):
    use_filter: bool = False
    crop: bool = False
    fill: bool = False
    height: int = Field(ge=0, default=400)
    width: int = Field(ge=0, default=400)


class TransformTextModel(BaseModel):
    use_filter: bool = False
    font_size: int = Field(ge=0, default=70)
    text: str = Field(max_length=100, default="")


class TransformRotateModel(BaseModel):
    use_filter: bool = False
    width: int = Field(ge=0, default=400)
    degree: int = Field(ge=-360, le=360, default=45)


class TransformBodyModel(BaseModel):
    circle: TransformCircleModel
    effect: TransformEffectModel
    resize: TransformResizeModel
    text: TransformTextModel
    rotate: TransformRotateModel