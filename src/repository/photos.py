from sqlalchemy.orm import Session
from src.database.models import Photo
from src.schemas import PhotoCreate, PhotoUpdate
from fastapi import File, UploadFile
from src.utils import upload_file

# Функція для створення нової фотографії


async def create_photo(photo: PhotoCreate, db: Session):
    image_url = await upload_file(photo.image)  # Завантаження файлу на сервер
    photo_data = photo.dict(exclude={"image"})
    photo_data["image_url"] = image_url
    db_photo = Photo(**photo_data)
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo

# Функція для отримання всіх фотографій


async def get_all_photos(skip: int, limit: int, db: Session):
    return db.query(Photo).offset(skip).limit(limit).all()

# Функція для отримання фотографії за її унікальним ідентифікатором


async def get_photo_by_id(photo_id: int, db: Session):
    return db.query(Photo).filter(Photo.id == photo_id).first()

# Функція для оновлення фотографії


async def update_photo(photo_id: int, updated_photo: PhotoUpdate, db: Session):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo:
        for key, value in updated_photo.dict().items():
            setattr(photo, key, value)
        db.commit()
    return photo

# Функція для видалення фотографії


async def delete_photo(photo_id: int, db: Session):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo:
        db.delete(photo)
        db.commit()
    return photo
