from fastapi import APIRouter, HTTPException, Depends, status, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict
from src.database.db import get_db
from src.database.models import User
from src.schemas import UserModel, UserResponse, TokenModel, UserDb, UserUpdate
from src.repository import users as repository_users
from src.authentication.auth import auth_service

router = APIRouter(prefix='/users', tags=["users"])


# Профіль користувача

@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user

# Редагування профілю користувача

@router.put("/edit", response_model=Dict[str, str])
async def edit_user_profile(
    user_update: UserUpdate,
    current_user: UserDb = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    user = await repository_users.get_user_by_id(current_user.id, db)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Здійснюємо оновлення даних користувача
    if user_update.email is not None:
        user.email = user_update.email
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
