from __future__ import annotations

from sqlalchemy.orm import Session
from src.database.models import User
from src.schemas.schemas import UserModel

async def get_user_by_id(user_id: int, db: Session) -> User:
    return db.query(User).filter(User.id == user_id).first()

async def get_user_by_email(email: str, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()

async def create_user(user: UserModel, db: Session):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

