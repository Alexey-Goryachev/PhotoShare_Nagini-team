from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from sqlalchemy.orm import Session
from typing import Dict
from src.database.db import get_db
from src.database.models import User
from src.schemas.schemas import UserModel, UserResponse, TokenModel, UserDb
from src.repository import users as repository_users
from src.services.auth import auth_service

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()

#Реєстрація
@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, db: Session = Depends(get_db)):
    """
    **The signup function creates a new user in the database.**
        **It takes an email and password as input, and returns a `UserResponse` object with the newly created user's information.**
        **If there is already an account associated with that email address, it will return a `409 Conflict error`.🔮**

    ___
    
    - **:param** 🧹 `body:` `UserModel:` Get the user model from the request body
    - **:param** 🧹 `db:` `Session:` Connect to the database \n
    **:return:** An object of type userresponse
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if "@" not in body.email:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid email")

    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    if body.roles[0] not in ["User", "Moderator", "Administrator"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invalid role")
    body.roles = ",".join(body.roles)
    body.password = auth_service.get_password_hash(body.password)
    body.is_active = True
    new_user = await repository_users.create_user(body, db)

    user_db = UserResponse(
        user=UserDb(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            photos_count=0,  # Set the initial value for photos_count
            created_at=new_user.created_at,
        ),
        role=body.roles[0],
        detail="User successfully created",
    )

    return user_db


#Логін
@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):  # Додайте залежність db
    """
    **The login function is used to authenticate a user.**🚂

    ___
    
    - **:param**⚡ `body:` OAuth2PasswordRequestForm: Receive the data from the request body\n
    - **:param**⚡ `db:` `Session:` Pass the database connection to the function\n
    **:return:** An object of the loginresponse class, which contains a jwt token
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is not active")

    # Генерація JWT токена
    access_token = auth_service.create_access_token(data={"sub": user.email, "message": "Logged successfully"})

    # Повертаємо об'єкт відповіді
    return {"access_token": access_token, "token_type": "bearer", "message": "Logged successfully"}

# Бан користувача

@router.post("/ban/{user_id}", response_model=Dict[str, str])
async def ban_user(
    user_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    **The `ban_user` function is used to ban a user from the system.**
        **This function requires an Administrator role to execute.**
        **The `user_id` parameter is required and must be a valid integer.💀**
    
    ___
    
    - **:param**🪄 `user_id:` `int:` Get the user id from the url
    - **:param**🪄 `current_user:` `User:` Get the current user
    - **:param**🪄 `db:` `Session:` Get the database session
    - **:param**🪄 : Get the user id of the user to be banned
    :return: A dictionary with a message
    """
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
async def unban_user(user_id: int, current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    **The `unban_user` function unban a user by id.**
        **Args:**
            **`user_id (int):` The id of the user to be unbanned.**
            **`current_user (User):` The currently logged in User object, which is used to check if the `current_user` has Administrator privileges.**
            **`db (Session):` A database session object that is used for querying and updating data in the database.  This function uses it to query for a specific User by their ID, and then update that User's `is_active`; field from False to True.**🧙🏻‍♂️
        
    ___
    
    - **:param**𐂂 user_id:** `int:` Get the user id from the request\n
    - **:param**𐂂 `current_user:` `User:` Get the current user from the database\n
    - **:param**𐂂 `db:` `Session:` Pass the database session to the function\n
    **:return:** A dictionary with a message
    """
    if current_user.roles != "Administrator":
        raise HTTPException(status_code=403, detail="Permission denied")

    user = await repository_users.get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    db.commit()
    db.refresh(user)
    return {"message": "User unbanned successfully"}


