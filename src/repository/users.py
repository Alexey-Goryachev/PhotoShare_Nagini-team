from __future__ import annotations

from sqlalchemy.orm import Session
from src.database.models import User
from src.schemas.schemas import UserModel

async def get_user_by_id(user_id: int, db: Session) -> User:
    """
    The get_user_by_id function returns a user object from the database based on the user's id.
        Args:
            user_id (int): The id of the desired User object.
            db (Session): A Session instance to query against.
    
    :param user_id: int: Specify the user id of the user we want to get
    :param db: Session: Pass in the database session to the function
    :return: A user object which has the following fields
    """
    return db.query(User).filter(User.id == user_id).first()

async def get_user_by_email(email: str, db: Session) -> User:
    """
    The get_user_by_email function takes in an email and a database session, then returns the user with that email.
        Args:
            email (str): The user's unique identifier.
            db (Session): A database session object to query from.
        Returns: 
            User: The user with the given id.
    
    :param email: str: Specify the email address of the user that we want to retrieve from our database
    :param db: Session: Pass in the database session to the function
    :return: The user object that matches the email address passed in
    """
    return db.query(User).filter(User.email == email).first()

async def create_user(user: UserModel, db: Session):
    """
    The create_user function creates a new user in the database.
        Args:
            user (UserModel): The UserModel object to be created.
            db (Session): The SQLAlchemy Session object used for querying the database.
    
    :param user: UserModel: Pass in the user object that is created when a new user registers
    :param db: Session: Create a database session
    :return: The newly created user object
    """
    
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

