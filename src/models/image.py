from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()


class Image(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    image_url = Column(String)


class ImageCreate(BaseModel):
    description: str
    image_url: str


class ImageFileCreate(BaseModel):
    description: str


class ImageFile(ImageFileCreate):
    id: int
    file_path: str
