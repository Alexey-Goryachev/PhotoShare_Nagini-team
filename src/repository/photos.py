from src.schemas import PhotoResponse
from sqlalchemy.orm import Session
from src.schemas import PhotoCreate, PhotoUpdate, PhotoListResponse
from fastapi import UploadFile
from src.utils import upload_file
from src.database.db import SessionLocal
from typing import List
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from cloudinary.uploader import destroy
from sqlalchemy.orm import Session
from src.database.models import Photo, User, Tag
from fastapi.exceptions import HTTPException
from datetime import datetime

from src.conf.config import settings
from src.repository.tags import create_tag


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

def get_public_id_from_image_url(image_url: str) -> str:
    parts = image_url.split("/")
    public_id = parts[-1].rsplit(".", 1)[0]
    public_id = public_id.replace('%40', '@')
    return public_id


def create_user_photo(photo: PhotoCreate, image: UploadFile, current_user: User, db: Session) -> PhotoResponse:
  
    init_cloudinary()
    # Створюю унікальний public_id на основі поточного часу
    timestamp = datetime.now().timestamp()
    public_id = f"{current_user.email}_{current_user.id}_{int(timestamp)}"

    image_bytes = image.file.read()
    upload_result = upload(image_bytes, public_id=public_id, overwrite=True)
    image_url = upload_result['secure_url']
    photo_data = photo.dict()
    photo_data["image_url"] = image_url
    photo_data["user_id"] = current_user.id 
    photo_data["public_id"] = public_id
    

    tag_objects = []
    for tag_name in photo_data['tags']:
        tag = db.query(Tag).filter(Tag.title == tag_name).first()
        if not tag:
            # Если тег не существует, создайте новый
            print(tag_name)
            # tag = await create_tag(str(tag_name), db, current_user)
            tag = Tag(title=tag_name, user_id=current_user.id)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        tag_objects.append(tag)
    print(tag_objects)
    photo_data['tags'] = tag_objects
    db_photo = Photo(**photo_data)
    print(db_photo)
    db_photo.tags = tag_objects
    # #Связывание фото с тегами
    # for tag in tag_objects:
    #     db_photo.tag.append(tag)

    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    
    photo_response_data = db_photo.__dict__
    photo_response_data.pop("_sa_instance_state", None)
    print(photo_response_data)
    return PhotoResponse(**photo_response_data)
    # db_photo_dict = db_photo.dict()
    # print(db_photo_dict)
    # return PhotoResponse(**db_photo_dict)



def get_user_photos(user_id: int, skip: int, limit: int, db: Session) -> PhotoListResponse:
    """
    Get user photos with optional filtering and pagination.

    :param user_id: int: (Optional) User ID for filtering photos by user.
    :param skip: int: Number of photos to skip.
    :param limit: int: Maximum number of photos to return.
    :param db: Session: Database session to use.
    :return: PhotoListResponse: List of photo responses.
    """

    photos_query = db.query(Photo)
    # Якщо user_id має значення None, не фільтруємо за user_id
    if user_id is not None:
        photos_query = photos_query.filter(Photo.user_id == user_id)
    photos = photos_query.offset(skip).limit(limit).all()
    
    return [PhotoResponse(
        id=photo.id,
        image_url=photo.image_url,
        description=photo.description,
        created_at=photo.created_at
    ) for photo in photos]



def get_user_photo_by_id(photo_id: int, db: Session, current_user: User) -> PhotoResponse:
    if "Administrator" in current_user.roles.split(","):
        user_id = None  # Адміністратор має доступ до фотографій будь-якого користувача
    else:
        user_id = current_user.id

    photo = db.query(Photo).filter(Photo.id == photo_id, (Photo.user_id == user_id) | (user_id == None)).first()
    if not photo:
        return None

    return PhotoResponse(
        id=photo.id,
        image_url=photo.image_url,
        description=photo.description,
        created_at=photo.created_at
    )




def get_user_photo_by_id(photo_id: int, db: Session) -> Photo:
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    return photo

def update_user_photo(photo: Photo, updated_photo: PhotoUpdate, db: Session) -> PhotoResponse:
    """
    Update a user's photo description.

    :param photo: Photo: The photo to update.
    :param updated_photo: PhotoUpdate: Data for updating the photo.
    :param db: Session: Database session to use.
    :return: PhotoResponse: The updated photo response.
    """
    if updated_photo.description is not None:
        photo.description = updated_photo.description
    photo.updated_at = datetime.utcnow()  # Оновлення поля updated_at
    db.commit()
    return PhotoResponse(
        id=photo.id,
        image_url=photo.image_url,
        description=photo.description,
        created_at=photo.created_at
    )



async def delete_user_photo(photo_id: int, user_id: int, is_admin: bool, db: Session):
    """
    Delete a user's photo, with access control for administrators and owners.

    :param photo_id: int: ID of the photo to delete.
    :param user_id: int: ID of the user requesting the delete.
    :param is_admin: bool: Indicates if the requester is an administrator.
    :param db: Session: Database session to use.
    :return: Photo: The deleted photo object.
    """
    
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    
    if not photo:
        return None  # Фото не знайдено
    
    if not is_admin and user_id != photo.user_id:
        raise HTTPException(status_code=403, detail="Permission denied")  # Користувач може видаляти лише свої фото
    
    # Видалення фотографії з Cloudinary за її public_id
    public_id = get_public_id_from_image_url(photo.image_url)

    init_cloudinary()
    destroy(public_id)
    destroy("PhotoshareApp_tr/" + public_id)
    destroy("PhotoshareApp_tr/" + public_id + '_qr')

    db.delete(photo)
    db.commit()
    
    return photo


