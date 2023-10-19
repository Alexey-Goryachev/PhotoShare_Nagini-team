from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from src.database.models import User, Photo
from src.schemas import UserModel, PhotoCreate, PhotoUpdate, PhotoResponse, PhotoListResponse
from src.authentication.auth import auth_service
from src.repository import users as repository_users
from src.repository import photos as repository_photos
from src.database.db import get_db

router = APIRouter(prefix="/photos", tags=["photos"])
security = HTTPBearer()


@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def create_user_photo(
    image: UploadFile = File(...),
    description: str = Form(...),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    photo_data = PhotoCreate(description=description)
    return repository_photos.create_user_photo(photo_data, image, db)


@router.get("/user-photos/", response_model=PhotoListResponse)
async def get_all_user_photos(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user or "Administrator" not in current_user.roles.split(","):
        raise HTTPException(status_code=403, detail="Permission denied")

    photos = await repository_photos.get_all_photos(skip, limit, db)
    return {"photos": photos}


@router.get("/user-photos/{photo_id}", response_model=PhotoResponse)
async def get_user_photo_by_id(
    photo_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user or "Administrator" not in current_user.roles.split(","):
        raise HTTPException(status_code=403, detail="Permission denied")

    photo = await repository_photos.get_photo_by_id(photo_id, db)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Фото не знайдено")
    return photo


@router.put("/user-photos/{photo_id}", response_model=PhotoResponse)
async def update_user_photo(
    photo_id: int,
    updated_photo: PhotoUpdate,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user or "Administrator" not in current_user.roles.split(","):
        raise HTTPException(status_code=403, detail="Permission denied")

    photo = await repository_photos.update_photo(photo_id, updated_photo, db)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Фото не знайдено")
    return photo


@router.delete("/user-photos/{photo_id}", response_model=PhotoResponse)
async def delete_user_photo(
    photo_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user or "Administrator" not in current_user.roles.split(","):
        raise HTTPException(status_code=403, detail="Permission denied")

    result = await repository_photos.delete_photo(photo_id, db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Фото не знайдено")

    response_data = {
        "id": result.id,
        "image_url": result.image_url,
        "description": result.description,
        "created_at": result.created_at
    }

    return response_data
