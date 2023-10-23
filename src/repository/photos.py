from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import UploadFile
import cloudinary
from cloudinary.uploader import upload
from cloudinary.uploader import destroy
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException

from src.database.models import Photo, User, Tag
from src.conf.config import settings
from src.schemas.schemas import PhotoCreate, PhotoUpdate, PhotoListResponse, TagResponse, PhotoResponse


def init_cloudinary():
    """
    The init_cloudinary function initializes the cloudinary library with the settings from our Django project's settings.py file.
    
    :return: A dictionary of the cloudinary configuration
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

def get_public_id_from_image_url(image_url: str) -> str:
    """
    The get_public_id_from_image_url function takes a Cloudinary image URL as input and returns the public ID of the image.
    
    :param image_url: str: Pass in the image url as a string
    :return: The public id of an image
    """
    parts = image_url.split("/")
    public_id = parts[-1].rsplit(".", 1)[0]
    public_id = public_id.replace('%40', '@')
    return public_id


def create_user_photo(photo: PhotoCreate, image: UploadFile, current_user: User, db: Session) -> PhotoResponse:
    """
    The create_user_photo function creates a new photo for the current user.
    
    :param photo: PhotoCreate: Create a new photo object
    :param image: UploadFile: Pass the image file to the function
    :param current_user: User: Get the user id of the current user
    :param db: Session: Access the database
    :return: A photoresponse object
    """
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
    
    tag_titles = [tag.strip() for tag in photo_data['tags'][0].split(",") if tag.strip()]
    if len(tag_titles) > 5:
        raise HTTPException(status_code=400, detail="Too many tags provided")
    tag_objects = []
    for tag_name in tag_titles:
        tag = db.query(Tag).filter(Tag.title == tag_name).first()
        if not tag:
            tag = Tag(title=tag_name, user_id=current_user.id)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        tag_objects.append(tag)
    photo_data['tags'] = tag_objects
    db_photo = Photo(**photo_data)
    db_photo.tags = tag_objects


    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)

    
    photo_response_data = db_photo.__dict__
    photo_response_data["tags"] = [TagResponse(id=tag.id, title=tag.title, created_at=tag.created_at) for tag in db_photo.tags]
    photo_response_data.pop("_sa_instance_state", None)

    return PhotoResponse(**photo_response_data)
   

def get_user_photos(user_id: int, skip: int, limit: int, db: Session) -> PhotoListResponse:
    """
    The get_user_photos function returns a list of photos for the specified user.
    If no user_id is provided, all photos are returned.
    
    
    :param user_id: int: Filter the photos by user_id
    :param skip: int: Skip the first n photos
    :param limit: int: Limit the number of photos returned
    :param db: Session: Pass the database session to the function
    :return: A list of photoresponse objects
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
        created_at=photo.created_at,
        updated_at=photo.updated_at,
        tags=[TagResponse(id=tag.id, title=tag.title, created_at=tag.created_at) for tag in photo.tags]
    ) for photo in photos]



def get_user_photo_by_id(photo_id: int, db: Session, current_user: User) -> PhotoResponse:
    """
    The get_user_photo_by_id function returns a PhotoResponse object for the photo with the specified ID.
    
    :param photo_id: int: Specify the photo id
    :param db: Session: Connect to the database
    :param current_user: User: Check if the user is an administrator
    :return: A photoresponse object
    """
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
        created_at=photo.created_at,
        updated_at=photo.updated_at,
        tags=[TagResponse(id=tag.id, title=tag.title, created_at=tag.created_at) for tag in photo.tags]
    )




def get_user_photo_by_id(photo_id: int, db: Session) -> Photo:
    """
    The get_user_photo_by_id function returns a photo object from the database based on its id.
        Args:
            photo_id (int): The id of the photo to be returned.
            db (Session): A session object for interacting with the database.
        Returns:
            Photo: A single Photo object from the database.
    
    :param photo_id: int: Identify the photo in the database
    :param db: Session: Pass the database session to the function
    :return: A photo object, which is a row from the database
    """
    
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    return photo

def update_user_photo(photo: Photo, updated_photo: PhotoUpdate, current_user: User, db: Session) -> PhotoResponse:
    """
    The update_user_photo function updates a photo in the database.
        Args:
            photo (Photo): The Photo object to be updated.
            updated_photo (PhotoUpdate): The new data for the Photo object.
            current_user (User): The user who is making this request, used to check permissions and ownership of the resource being modified.
            db (Session): A connection to our database, used for querying and updating records in our tables.
    
    :param photo: Photo: Get the photo object from the database
    :param updated_photo: PhotoUpdate: Update the photo
    :param current_user: User: Get the user id of the current user
    :param db: Session: Access the database
    :return: A photoresponse object
    """
    if updated_photo.description is not None:
        photo.description = updated_photo.description

    if updated_photo.tags:
        tag_objects = []
        for tag_name in updated_photo.tags:
            tag = db.query(Tag).filter(Tag.title == tag_name,).first()
            if not tag:
                tag = Tag(title=tag_name, user_id=current_user.id)
                db.add(tag)
            tag_objects.append(tag)
        photo.tags = tag_objects

    photo.updated_at = datetime.utcnow()  # Оновлення поля updated_at
    db.commit()
    return PhotoResponse(
        id=photo.id,
        image_url=photo.image_url,
        description=photo.description,
        created_at=photo.created_at,
        updated_at=photo.updated_at,
        tags=[TagResponse(id=tag.id, title=tag.title, created_at=tag.created_at) for tag in photo.tags]
    )



async def delete_user_photo(photo_id: int, user_id: int, is_admin: bool, db: Session):
    """
    The delete_user_photo function deletes a photo from the database and Cloudinary.
        Args:
            photo_id (int): The id of the photo to be deleted.
            user_id (int): The id of the user who is deleting this photo.
            is_admin (bool): Whether or not this user has admin privileges.
        Returns: 
            Photo object if successful, None otherwise.
    
    :param photo_id: int: Specify the id of the photo to be deleted
    :param user_id: int: Check if the user is authorized to delete the photo
    :param is_admin: bool: Check if the user is an admin or not
    :param db: Session: Pass the database session to the function
    :return: The deleted photo
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


