from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Dict
from src.database.db import get_db
from src.database import models
from src.database.models import User, Photo
from src.repository.photos import get_user_photos
from src.schemas.schemas import UserDb, UserUpdate, AdminUserPatch
from src.repository import users as repository_users
from src.services.auth import auth_service

router = APIRouter(tags=["users"])

# Рахуємо фото
def get_user_photos_count(user_id: int, db: Session) -> int:
    # Отримуємо кількість фотографій для користувача
    photos_count = db.query(Photo).filter(Photo.user_id == user_id).count()
    return photos_count



# Профіль користувача

@router.get("/me/", response_model=UserDb)
async def read_users_me(
    current_user: UserDb = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    # Отримуємо кількість фотографій для поточного користувача
    photos_count = get_user_photos_count(current_user.id, db)

    # Додаємо кількість фотографій до відповіді
    current_user.photos_count = photos_count

    return current_user

# Редагування профілю користувача

@router.put("/edit", response_model=Dict[str, str])
async def edit_user_profile(
    user_update: UserUpdate,
    current_user: UserDb = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    # Отримуємо інформацію про користувача з бази даних
    user = await repository_users.get_user_by_id(current_user.id, db)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Якщо користувач хоче змінити свою електронну адресу
    if user_update.email is not None:
        # Перевіряємо, чи існує користувач із новою електронною адресою
        existing_user = await repository_users.get_user_by_email(user_update.email, db)
        if existing_user and existing_user.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This user already exists. Please enter another email",
            )
        user.email = user_update.email

    # Здійснюємо оновлення даних користувача
    if user_update.username is not None:
        user.username = user_update.username

    # Якщо користувач вказав новий пароль, то оновлюємо його
    if user_update.password is not None:
        # Отримуємо реальне значення пароля з SecretStr
        password = user_update.password.get_secret_value()
        user.password = auth_service.get_password_hash(password)

    db.commit()
    db.refresh(user)

    return {"message": "Data changed successfully"}


# Редагування профілю користувача

@router.patch("/patch/{user_id}", response_model=Dict[str, str])
async def patch_user_profile(
    user_id: int,
    user_update: AdminUserPatch,
    current_user: UserDb = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user or "Administrator" not in current_user.roles.split(","):
        raise HTTPException(status_code=403, detail="Permission denied")

    # Получаем информацию о пользователе из базы данных
    user = await repository_users.get_user_by_id(user_id, db)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Если пользователь хочет изменить свою электронную адресу
    if user_update.email is not None:
        # Проверяем, существует ли пользователь с новым электронным адресом
        existing_user = await repository_users.get_user_by_email(user_update.email, db)
        if existing_user and existing_user.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This user already exists. Please enter another email",
            )
        user.email = user_update.email

    # Обновляем данные пользователя
    if user_update.username is not None:
        user.username = user_update.username

    # Если пользователь указал новый пароль, то обновляем его
    if user_update.password is not None:
        # Получаем реальное значение пароля из SecretStr
        password = user_update.password.get_secret_value()
        user.password = auth_service.get_password_hash(password)

    # Если пользователь указал новый статус, то обновляем его
    if user_update.is_active is not None:
        user.is_active = user_update.is_active

    db.commit()
    db.refresh(user)

    return {"message": "Data changed successfully"}
