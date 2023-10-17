from sqlalchemy import Column, Integer, String, Boolean, func, Table, UniqueConstraint, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import Enum

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    roles = Column(Enum("User", "Moderator", "Administrator", name="user_roles"), default="User")
    created_at = Column('created_at', DateTime, default=func.now())

    # відносини для фотографій і користувача
    photos = relationship("Photo", back_populates="user")



photo_2_tag = Table("photo_2_tag", Base.metadata,
                    Column('id', Integer, primary_key=True),
                    Column('photo_id', Integer, ForeignKey('photos.id', ondelete='CASCADE')),
                    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE')),
                    )


class Photo(Base):
    __tablename__ = "photos"
    id = Column(Integer, primary_key=True)
    image_url = Column(String(300))
    description = Column(String(500), nullable=True)
    tag = relationship('Tag', secondary=photo_2_tag, backref='photos')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
    # Зовнішній ключ для зв'язку з користувачем
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), default=None)

    # Зв'язок з користувачем
    user = relationship("User", back_populates="photos")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    photos_id = Column('photos_id', ForeignKey('photos.id', ondelete='CASCADE'), default=None)
    update_status = Column(Boolean, default=False)

    user = relationship('User', backref="comments")
    post = relationship('Photo', backref="comments")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    title = Column(String(25), nullable=False, unique=True)
    created_at = Column(DateTime, default=func.now())
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)

    user = relationship('User', backref="tags")
