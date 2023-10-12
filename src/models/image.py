
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

# Оголошення моделі Image, яка відображає таблицю 'photos' в базі даних


class Image(Base):
    __tablename__ = "photos"

    # Поля таблиці
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    image_url = Column(String)

# Клас ImageCreate використовується для валідації даних, які передаються для створення нового запису


class ImageCreate(BaseModel):
    description: str
    image_url: str

# Клас ImageFileCreate є допоміжним та використовується для операцій з файлами


class ImageFileCreate(BaseModel):
    description: str

# Клас ImageFile успадковує ImageFileCreate та додає поля для бази даних


class ImageFile(ImageFileCreate):
    id: int
    file_path: str
