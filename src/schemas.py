from datetime import datetime
from typing import List, Optional
from enum import Enum
from fastapi import UploadFile
from pydantic import BaseModel, EmailStr, Field
from typing import List
from enum import Enum
from fastapi import UploadFile
from pydantic import BaseModel, EmailStr, constr, SecretStr
from pydantic import BaseModel, EmailStr, Field


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
        from_attributes = True


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
    #TODO
    image_transform: str
    qr_transform: str
    public_id: str
########################

class PhotoCreate(BaseModel):
    description: str
    # image: UploadFile


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
    qr_transform: str

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
# =======

class CommentBase(BaseModel):
    text: str = Field(max_length=500)


class CommentModel(CommentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    photos_id: int
    update_status: bool = False

    class Config:
        from_attributes = True


class CommentUpdate(CommentModel):
    update_status: bool = True
    updated_at: datetime

    class Config:
        from_attributes = True


# ======

class TagBase(BaseModel):
    title: str = Field(max_length=50)


class TagModel(TagBase):
    pass

    class Config:
        from_attributes = True

class TagResponse(TagBase):
    id: int
    # user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
