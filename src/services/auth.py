from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from starlette import status

from src.database.db import get_db
from src.database.models import User
from fastapi import APIRouter

router = APIRouter()

# Хешування пароля
class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        The verify_password function takes a plain-text password and the hashed version of that password,
            and returns True if they match, False otherwise.
        
        
        :param self: Make the method work for a specific instance of the class
        :param plain_password: Pass in the plain text password that is entered by the user
        :param hashed_password: Verify the password
        :return: A boolean value
        """
        
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password as an argument and returns the hash of that password.
            The function uses the pwd_context object to generate a hash from the given password.
        
        :param self: Represent the instance of the class
        :param password: str: Pass in the password that is being hashed
        :return: A hash of the password
        """ 
        return self.pwd_context.hash(password)


    SECRET_KEY = "secret_key"
    ALGORITHM = "HS256"

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


    # Генерація токена
    def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_access_token function creates a JWT token with the given payload.
            
        
        :param self: Represent the instance of the class
        :param data: dict: Store the data that will be encoded in the jwt
        :param expires_delta: Optional[float]: Set the expiration time for the token
        :return: An encoded jwt
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        The get_current_user function is a dependency that will be used in the UserRouter class.
        It takes a token as an argument and returns the user object associated with that token.
        
        :param self: Represent the instance of a class
        :param token: str: Pass the jwt token to the function
        :param db: Session: Access the database
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Декодування JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            if email is None:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user: User = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
        return user

auth_service = Auth()


