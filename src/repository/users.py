from __future__ import annotations

from sqlalchemy.orm import Session
from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()

async def create_user(user: UserModel, db: Session):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# async def create_user(body: UserModel, db: Session) -> User:
#     new_user = User(**body.dict())
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user
