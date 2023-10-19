from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import Form, File, UploadFile
from src.database.db import get_db
from src.schemas import PhotoCreate, PhotoResponse, PhotoListResponse, PhotoUpdate
from src.repository import photos as repository_photos
from src.database.db import SessionLocal
from src.repository.photos import get_all_photos
from starlette.responses import JSONResponse
from src.database.models import Photo, User
from src.repository import photos as repository_photos
from src.schemas import PhotoTransform, TransformBodyModel, PhotoLinkTransform
from src.services.photos import transform_image, create_link_transform_image
from src.authentication.auth import auth_service

router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def create_photo(
    image: UploadFile = File(...),
    description: str = Form(...),

    db: Session = Depends(get_db)
):
    photo_data = PhotoCreate(description=description)
    return repository_photos.create_photo(photo_data, image, db)


@router.get("/", response_model=PhotoListResponse)
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

@router.patch('/transformation', response_model=PhotoTransform)
async def photo_transformation(photo_id: int, body: TransformBodyModel, db: Session=Depends(get_db)):
    photo = await transform_image(photo_id, body, db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    if isinstance(photo, Photo):
        raise HTTPException(status_code=status.HTTP_200_OK, detail="You don't choose type transformation")
    return {"id": photo_id, "image_transform": photo,  "detail": "Your image successfully transform"}

@router.post('/create_link_for_transformation', response_model=PhotoLinkTransform)
async def create_link_for_image_transformation(photo_id: int, db: Session=Depends(get_db)):
    result = await create_link_transform_image(photo_id, db)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return result