from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from src.database.models import User, Photo
from src.schemas import (
    UserModel,
    PhotoCreate,
    PhotoUpdate,
    PhotoResponse,
    PhotoListResponse,
)
from src.authentication.auth import auth_service
from src.repository import users as repository_users
from src.repository import photos as repository_photos
from src.database.db import get_db


from src.schemas import PhotoCreate, PhotoResponse, PhotoListResponse, PhotoUpdate
from src.repository import photos as repository_photos
from src.database.db import SessionLocal

# from src.repository.photos import get_all_photos
from starlette.responses import JSONResponse
from src.database.models import Photo, User
from src.repository import photos as repository_photos
from src.schemas import PhotoTransform, TransformBodyModel, PhotoLinkTransform
from src.services.photos import transform_image, create_link_transform_image
from src.authentication.auth import auth_service

router = APIRouter(prefix="/photos", tags=["photos"])
security = HTTPBearer()


@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def create_user_photo(
    image: UploadFile = File(...),
    description: str = Form(...),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    **Create a new user photo🐍**\n
    ___
    - **:param**🪄 `image`: UploadFile: The image to upload.\n
    - **:param**🪄 `description`: str: The description of the photo.\n
    - **:param**🪄 `current_user`: User: The currently authenticated user.\n
    - **:param**🪄 `db`: Session: The database session.\n
    :return: PhotoResponse: The created photo response.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    photo_data = PhotoCreate(description=description)
    return repository_photos.create_user_photo(photo_data, image, db, current_user)


@router.get("/user-photos/", response_model=PhotoListResponse)
async def get_user_photos(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    **Get a list of user photos with optional filtering and pagination🔮**\n

    - **:param**⚡ `skip`: int: Number of photos to skip.\n
    - **:param**⚡ `limit`: int: Maximum number of photos to return.\n
    - **:param**⚡ `db`: Session: The database session.\n
    - **:param**⚡ `current_user`: User: The currently authenticated user.\n
    :return: PhotoListResponse: List of photo responses.
    """
    if "Administrator" in current_user.roles:
        user_id = None  # Адміністратор має доступ до фотографій будь-якого користувача
    else:
        user_id = current_user.id

    photos = repository_photos.get_user_photos(user_id, skip, limit, db)
    return {"photos": photos}


@router.get("/user-photos/{photo_id}", response_model=PhotoResponse)
async def get_user_photo_by_id(
    photo_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    **Get a user photo by ID🪶**\n

    - **:param**🧹 `photo_id`: int: ID of the photo to retrieve.\n
    - **:param**🧹 `current_user`: User: The currently authenticated user.\n
    - **:param**🧹 `db`: Session: The database session.\n
    :return: PhotoResponse: The requested photo response.\n
    """
    if "Administrator" in current_user.roles.split(","):
        user_id = None  # Адміністратор має доступ до фотографій будь-якого користувача
    else:
        user_id = current_user.id

    photo = (
        db.query(Photo)
        .filter(Photo.id == photo_id, (Photo.user_id == user_id) | (user_id == None))
        .first()
    )

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )

    return PhotoResponse(
        id=photo.id,
        image_url=photo.image_url,
        description=photo.description,
        created_at=photo.created_at,
    )


@router.put("/user-photos/{photo_id}", response_model=PhotoResponse)
async def update_user_photo(
    photo_id: int,
    updated_photo: PhotoUpdate,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    **Update a user's photo description🦉**\n

    - **:param**⚯ `photo_id`: int: ID of the photo to update.\n
    - **:param**⚯ `updated_photo`: PhotoUpdate: Data for updating the photo.\n
    - **:param**⚯ `current_user`: User: The currently authenticated user.\n
    - **:param**⚯ `db`: Session: The database session.\n
    :return: PhotoResponse: The updated photo response.
    """
    photo = repository_photos.get_user_photo_by_id(photo_id, db)

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )

    if not (
        current_user
        and ("Administrator" in current_user.roles.split(","))
        or current_user.id == photo.user_id
    ):
        raise HTTPException(status_code=403, detail="Permission denied")

    updated_photo = repository_photos.update_user_photo(photo, updated_photo, db)
    return updated_photo


@router.delete("/user-photos/{photo_id}", response_model=PhotoResponse)
async def delete_user_photo(
    photo_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    **Delete a user's photo with access control for administrators and owners🧙🏻‍♂️**\n

    - **:param**🧹 `photo_id`: int: ID of the photo to delete.**\n
    - **:param**🧹 `current_user`: User: The currently authenticated user.**\n
    - **:param**🧹 `db`: Session: The database session.**\n
    :return: PhotoResponse: The deleted photo response.
    """
    if not current_user:
        raise HTTPException(
            status_code=403, detail="Permission denied"
        )  # Користувач повинен бути авторизований для видалення фото

    is_admin = "Administrator" in current_user.roles.split(",")

    result = await repository_photos.delete_user_photo(
        photo_id, current_user.id, is_admin, db
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )

    response_data = {
        "id": result.id,
        "image_url": result.image_url,
        "description": result.description,
        "created_at": result.created_at,
    }

    return response_data


@router.patch("/transformation", response_model=PhotoTransform)
async def photo_transformation(
    photo_id: int,
    body: TransformBodyModel,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    photo = await transform_image(photo_id, body, current_user, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
        )
    if isinstance(photo, Photo):
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="You don't choose type transformation",
        )
    return {
        "id": photo_id,
        "image_transform": photo,
        "detail": "Your image successfully transform",
    }


@router.post("/create_link_for_transformation", response_model=PhotoLinkTransform)
async def create_link_for_image_transformation(
    photo_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    result = await create_link_transform_image(photo_id, current_user, db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
        )
    return result
