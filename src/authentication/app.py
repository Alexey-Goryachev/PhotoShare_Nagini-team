from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from enum import Enum
from typing import List
from src.authentication.auth import create_access_token, get_current_user, Auth
from src.database.db import get_db
from src.database.models import User
from src.schemas import Role

app = FastAPI()
hash_handler = Auth()

class Role(str, Enum):
    User = "User"
    Moderator = "Moderator"
    Administrator = "Administrator"


class UserModel(BaseModel):
    username: str
    email: str
    password: str
    roles: List[Role] = [Role.User]

# Реєстрація
@app.post("/signup")
async def signup(body: UserModel, db: Session = Depends(get_db)):
    exist_user = db.query(User).filter(User.email == body.username).first()
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    if body.roles[0] not in [role.value for role in Role]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")
    new_user = User(email=body.username, password=hash_handler.get_password_hash(body.password), role=body.roles[0])
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"new_user": new_user.email, "role": new_user.role}

#Логін
@app.post("/login")
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not hash_handler.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Генеруємо JWT
    access_token = create_access_token(data={"sub": user.email, "message": "Logged successfully"})
    return {"access_token": access_token, "token_type": "bearer", "message": "Logged successfully"}


@app.get("/")
async def root():
    return {"message": "Hello User"}

@app.get("/roles", response_model=List[Role])
async def get_roles():
    return list(Role)


@app.get("/secret")
async def read_item(current_user: User = Depends(get_current_user)):
    return {"message": 'secret router', "owner": current_user.email}