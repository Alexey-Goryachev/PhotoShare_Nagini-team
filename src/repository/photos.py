# import cloudinary.uploader
from src.schemas import PhotoResponse
from sqlalchemy.orm import Session
from src.database.models import Photo
from src.schemas import PhotoCreate, PhotoUpdate, PhotoListResponse
from fastapi import UploadFile
from src.utils import upload_file
from src.database.db import SessionLocal
from src.database.models import Photo
from typing import List
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from faker import Faker
from cloudinary.uploader import destroy
from sqlalchemy.orm import Session
from src.database.models import Photo


cloudinary.config(
    cloud_name="dpqnfhenr",
    api_key="679423711358256",
    api_secret="qWDJar70AfWF-iGLiKw64EOPxKI"
)


def init_cloudinary():
    cloudinary.config(
        cloud_name="dpqnfhenr",
        api_key="679423711358256",
        api_secret="qWDJar70AfWF-iGLiKw64EOPxKI"
    )


def create_user_photo(photo: PhotoCreate, image: UploadFile, db: Session) -> PhotoResponse:
    public_id = Faker().first_name()

    # Отримати байтові дані з об'єкта UploadFile
    image_bytes = image.file.read()

    # Завантажити байтові дані на Cloudinary
    upload_result = upload(image_bytes, public_id=public_id, overwrite=True)
    image_url = upload_result['secure_url']

    # Створити об'єкт фотографії для збереження в базі даних
    photo_data = photo.dict()
    photo_data["image_url"] = image_url
    db_photo = Photo(**photo_data)

    # Зберегти фотографію в базі даних
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)

    photo_response_data = db_photo.__dict__
    photo_response_data.pop("_sa_instance_state", None)

    return PhotoResponse(**photo_response_data)


def get_all_user_photos(skip: int, limit: int, db: Session) -> PhotoListResponse:
    photos = db.query(Photo).offset(skip).limit(limit).all()
    return [PhotoResponse(
        id=photo.id,
        image_url=photo.image_url,
        description=photo.description,
        created_at=photo.created_at
    ) for photo in photos]


def get_user_photo_by_id(photo_id: int, db: Session) -> PhotoResponse:
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        return None
    return PhotoResponse(
        id=photo.id,
        image_url=photo.image_url,
        description=photo.description,
        created_at=photo.created_at
    )


async def get_all_user_photos(skip: int, limit: int, db: Session):
    return db.query(Photo).offset(skip).limit(limit).all()


async def get_user_photo_by_id(photo_id: int, db: Session):
    return db.query(Photo).filter(Photo.id == photo_id).first()


async def update_user_photo(photo_id: int, updated_photo: PhotoUpdate, db: Session):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo:
        # Перевірка, чи в `updated_photo` є значення для `description`
        if updated_photo.description is not None:
            photo.description = updated_photo.description
        db.commit()
        return PhotoResponse(id=photo.id, image_url=photo.image_url, description=photo.description, created_at=photo.created_at)


def get_public_id_from_image_url(image_url: str) -> str:
    # Розділити URL за символом "/" і вибрати останню частину як public_id
    public_id = image_url.split("/")[-1].split(".")[0]
    return public_id


async def delete_user_photo(photo_id: int, db: Session):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo:
        # Видалення фотографії з Cloudinary за її public_id
        public_id = get_public_id_from_image_url(photo.image_url)
        destroy(public_id)

        db.delete(photo)
        db.commit()
    return photo
