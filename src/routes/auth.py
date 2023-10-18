from fastapi import APIRouter, HTTPException, Depends, status, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import Dict
from src.database.db import get_db
from src.database.models import User
from src.schemas import UserModel, UserResponse, TokenModel
from src.repository import users as repository_users
from src.authentication.auth import auth_service, create_access_token, get_current_user

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()

#Реєстрація
@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, db: Session = Depends(get_db)):
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if "@" not in body.email:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid email")

    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    if body.roles[0] not in ["User", "Moderator", "Administrator"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invalid role")
    body.roles = ",".join(body.roles)
    body.password = auth_service.get_password_hash(body.password)
    body.is_active = True
    new_user = await repository_users.create_user(body, db)
    return {"user": new_user, "role": body.roles[0], "detail": "User successfully created"}


#Логін
@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):  # Додайте залежність db
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is not active")

    # Генерація JWT токена
    access_token = create_access_token(data={"sub": user.email, "message": "Logged successfully"})

    # Повертаємо об'єкт відповіді
    return {"access_token": access_token, "token_type": "bearer", "message": "Logged successfully"}

# Бан користувача

@router.post("/ban/{user_id}", response_model=Dict[str, str])
async def ban_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user or "Administrator" not in current_user.roles.split(","):
        raise HTTPException(status_code=403, detail="Permission denied")

    user = await repository_users.get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()
    db.refresh(user)
    return {"message": "User banned successfully"}

# Анбан користувача

@router.delete("/unban/{user_id}", response_model=Dict[str, str])
async def unban_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.roles != "Administrator":
        raise HTTPException(status_code=403, detail="Permission denied")

    user = await repository_users.get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    db.commit()
    db.refresh(user)
    return {"message": "User unbanned successfully"}

