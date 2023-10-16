from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import Form, File, UploadFile
from src.database.db import get_db
from src.schemas import PhotoCreate, PhotoResponse, PhotoListResponse, PhotoUpdate
from src.repository import photos as repository_photos
from src.database.db import SessionLocal
from src.repository.photos import get_all_photos
from starlette.responses import JSONResponse
from src.database.models import Photo


router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def create_photo(
    image: UploadFile = File(...),
    description: str = Form(...),
    db: Session = Depends(get_db)
):
    return await repository_photos.create_photo(PhotoCreate(description=description, image=image), db)


@router.get("/photos/", response_model=PhotoListResponse)
async def get_photos(skip: int = 0, limit: int = 10):
    db = SessionLocal()
    photos = repository_photos.get_photos(db, skip=skip, limit=limit)
    return {"photos": photos}


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(
    photo_id: int,
    db: Session = Depends(get_db)
):
    photo_data = repository_photos.get_photo_response(photo_id, db)
    if not photo_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Фото не знайдено")
    return photo_data


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
    result = await repository_photos.delete_photo(photo_id, db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    # Створено словник, який відповідає моделі PhotoResponse
    response_data = {
        "id": result.id,
        "image_url": result.image_url,
        "description": result.description,
        "created_at": result.created_at
    }

    return response_data
