from sqlalchemy import Column, Integer, String, Boolean, func, Table, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import Enum
from fastapi import File, UploadFile
from typing import List
from pydantic import BaseModel


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    roles = Column(Enum("User", "Moderator", "Administrator",
                   name="user_roles"), default="User")
    created_at = Column('created_at', DateTime, default=func.now())
    is_active = Column(Boolean, default=True)


# відносини для фотографій і користувача
    photos = relationship("Photo", back_populates="user")


class Photo(Base):
    __tablename__ = "photos"
    id = Column(Integer, primary_key=True)
    image_url = Column(String(300))
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
    # Зовнішній ключ для зв'язку з користувачем
    user_id = Column(Integer, ForeignKey("users.id"))

    # Зв'язок з користувачем
    user = relationship("User", back_populates="photos")
