from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import Form, File, UploadFile  # Додано імпорти

from src.database.db import get_db
from src.schemas import PhotoCreate, PhotoResponse, PhotoListResponse, PhotoUpdate
from src.repository import photos as repository_photos

router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def create_photo(
    image: UploadFile = File(...),  # Додано параметр для завантаження файлу
    description: str = Form(...),
    db: Session = Depends(get_db)
):
    # Обробка завантаження зображення та створення фотографії
    # Додайте код для обробки завантаження зображення і збереження інформації про фото в базі даних
    return await repository_photos.create_photo(PhotoCreate(image_url=image.filename, description=description), db)


@router.get("/", response_model=PhotoListResponse)
async def get_photos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    photos = await repository_photos.get_all_photos(skip, limit, db)
    return {"photos": photos}


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(
    photo_id: int,
    db: Session = Depends(get_db)
):
    photo = await repository_photos.get_photo_by_id(photo_id, db)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Фото не знайдено")
    return photo


@router.put("/{photo_id}", response_model=PhotoResponse)
async def update_photo(
    photo_id: int,
    updated_photo: PhotoUpdate,
    db: Session = Depends(get_db)
):
    photo = await repository_photos.update_photo(photo_id, updated_photo, db)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Фото не знайдено")
    return photo


@router.delete("/{photo_id}", response_model=PhotoResponse)
async def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db)
):
    photo = await repository_photos.delete_photo(photo_id, db)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Фото не знайдено")
    return photo
