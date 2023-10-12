from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

# Модель для зображення (Image)


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    image_url = Column(String)

# Модель для створення зображення


class ImageCreate(BaseModel):
    description: str
    image_url: str
