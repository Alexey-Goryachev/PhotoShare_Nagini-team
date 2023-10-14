from src.schemas import PhotoResponse
from sqlalchemy.orm import Session
from src.database.models import Photo
from src.schemas import PhotoCreate, PhotoUpdate
from fastapi import UploadFile
from src.utils import upload_file
from src.database.db import SessionLocal
from src.database.models import Photo
from typing import List


def get_photos(db: SessionLocal, skip: int = 0, limit: int = 10) -> List[PhotoResponse]:
    photos = db.query(Photo).offset(skip).limit(limit).all()
    return [PhotoResponse(
        id=photo.id,
        image_url=photo.image_url,
        description=photo.description,
        created_at=photo.created_at
    ) for photo in photos]


def get_photo_response(photo_id: int, db: Session):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        return None
    return PhotoResponse(
        id=photo.id,
        image_url=photo.image_url,
        description=photo.description,
        created_at=photo.created_at
    )


async def create_photo(photo: PhotoCreate, db: Session):
    image_url = await upload_file(photo.image)  # Завантаження файлу на сервер
    photo_data = photo.dict(exclude={"image"})
    photo_data["image_url"] = image_url
    db_photo = Photo(**photo_data)
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)

    photo_response_data = db_photo.__dict__
    # Видаляємо SQLAlchemy internal state
    photo_response_data.pop("_sa_instance_state", None)

    return PhotoResponse(**photo_response_data)


async def get_all_photos(skip: int, limit: int, db: Session):
    return db.query(Photo).offset(skip).limit(limit).all()


async def get_photo_by_id(photo_id: int, db: Session):
    return db.query(Photo).filter(Photo.id == photo_id).first()


async def update_photo(photo_id: int, updated_photo: PhotoUpdate, db: Session):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo:
        # Перевірка, чи в `updated_photo` є значення для `description`
        if updated_photo.description is not None:
            photo.description = updated_photo.description
        db.commit()
        return PhotoResponse(id=photo.id, image_url=photo.image_url, description=photo.description, created_at=photo.created_at)


async def delete_photo(photo_id: int, db: Session):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo:
        db.delete(photo)
        db.commit()
        return None
    return None
