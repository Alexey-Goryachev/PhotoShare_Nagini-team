import cloudinary.uploader
from src.schemas import PhotoResponse
from sqlalchemy.orm import Session
from src.database.models import Photo
from src.schemas import PhotoCreate, PhotoUpdate
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
from src.conf.config import settings


# cloudinary.config(
#     cloud_name="dpqnfhenr",
#     api_key="679423711358256",
#     api_secret="qWDJar70AfWF-iGLiKw64EOPxKI"
# )


def init_cloudinary():
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )


def create_photo(photo: PhotoCreate, image: UploadFile, db: Session) -> PhotoResponse:
    init_cloudinary()
    public_id = Faker().first_name()

    # Отримати байтові дані з об'єкта UploadFile
    image_bytes = image.file.read()

    # Завантажити байтові дані на Cloudinary
    upload_result = upload(image_bytes, public_id=public_id, overwrite=True)
    image_url = upload_result['secure_url']

    # Створити об'єкт фотографії для збереження в базі даних
    photo_data = photo.dict()
    photo_data["image_url"] = image_url
    photo_data["public_id"] = public_id
    db_photo = Photo(**photo_data)

    # Зберегти фотографію в базі даних
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)

    photo_response_data = db_photo.__dict__
    photo_response_data.pop("_sa_instance_state", None)
    print(photo_response_data)
    return PhotoResponse(**photo_response_data)


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


def get_public_id_from_image_url(image_url: str) -> str:
    # Розділити URL за символом "/" і вибрати останню частину як public_id
    public_id = image_url.split("/")[-1].split(".")[0]
    return public_id


async def delete_photo(photo_id: int, db: Session):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo:
        # Видалення фотографії з Cloudinary за її public_id
        public_id = get_public_id_from_image_url(photo.image_url)
        public_id_tr = get_public_id_from_image_url(photo.image_transform)
        destroy(public_id)
        destroy("PhotoshareApp_tr/" + public_id_tr)

        db.delete(photo)
        db.commit()
    return photo
