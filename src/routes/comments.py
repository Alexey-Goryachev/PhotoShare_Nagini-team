from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from src.database.db import get_db
from src.schemas.schemas import CommentBase, CommentUpdate, CommentModel
from src.repository import comments as repository_comments
from src.services.auth import auth_service
from src.conf import messages as message
from src.services.roles import RoleChecker
from src.database.models import User
from src.schemas.schemas import Role

router = APIRouter(prefix='/comments', tags=["comments"])

# Set permissions by RoleChecker for current route
allowed_get_comments = RoleChecker([Role.Administrator, Role.Moderator, Role.User])
allowed_create_comments = RoleChecker([Role.Administrator, Role.Moderator, Role.User])
allowed_update_comments = RoleChecker([Role.Administrator, Role.Moderator, Role.User])
allowed_remove_comments = RoleChecker([Role.Administrator, Role.Moderator])


@router.post("/{photos_id}", response_model=CommentModel, dependencies=[Depends(allowed_create_comments)])
async def create_comment(photos_id: int,
                         body: CommentBase,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)
                         ):
    """
    The `create_comment function` creates a new comment for the photo with the given id.\n\n
    **The body of the comment is passed in as JSON data, and must contain a `body` field.
    The user who created this comment will be set to `current_user`.**
    ___

    - **:param** `photos_id`: _int_: Specify the post that the comment is being created for\n
    - **:param** `body`: _CommentBase_: Pass the data from the request body to the function\n
    - **:param** `db`: _Session_: Pass the database session to the repository layer\n
    - **:param** `current_user`: _User_: Get the current user\n
    :return: A comment object, which is then serialized as json
    """
    new_comment = await repository_comments.create_comment(photos_id, body, db, current_user)
    return new_comment


@router.put("/{comment_id}", response_model=CommentUpdate, dependencies=[Depends(allowed_update_comments)])
async def edit_comment(comment_id: int,
                       body: CommentBase,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)
                       ):
    """
    The `edit_comment function` allows a user to edit their own comment.\n\n
    **The function takes in the `comment_id`, body and db as parameters.
    It then calls the edit_comment function from `repository_comments` which returns an edited comment object if successful or `None` otherwise.
    If it is unsuccessful, it raises a 404 error with detail message `COMM_NOT_FOUND`.**

    ___

    - **:param** `comment_id`: _int_: Identify the comment to be edited\n
    - **:param** `body`: _CommentBase_: Pass the comment body to the edit_comment function\n
    - **:param** `db`: _Session_: Get the database session\n
    - **:param** `current_user`: _User_: Get the user who is currently logged in\n
    :return: None, but the function expects a CommentBase object\n
    """
    edited_comment = await repository_comments.edit_comment(comment_id, body, db, current_user)
    if edited_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.COMM_NOT_FOUND)
    return edited_comment


@router.delete("/{comment_id}", response_model=CommentModel, dependencies=[Depends(allowed_remove_comments)])
async def delete_comment(comment_id: int,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)
                         ):
    """
    The `delete_comment function` deletes a comment from the database.\n\n
    **The function takes in an integer representing the id of the comment to be deleted,
    and returns a dictionary containing information about that comment.**

    ___

    - **:param** `comment_id`: _int_: Specify the comment that is to be deleted
    - **:param** `db`: _Session_: Get the database session from the dependency
    - **:param** `current_user`: _User_: Check if the user is logged in
    :return: The deleted comment
    """
    deleted_comment = await repository_comments.delete_comment(comment_id, db, current_user)
    if deleted_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.COMM_NOT_FOUND)
    return deleted_comment


@router.get("/{comment_id}", response_model=CommentModel, dependencies=[Depends(allowed_get_comments)])
async def single_comment(comment_id: int,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)
                         ):
    """
    The `single_comment function` returns a single comment from the database.\n\n
    **The function takes in an integer representing the id of the comment to be returned,
    and two optional parameters: `db` and `current_user`. If no db is provided, it will use
    `get_db()` to create a new connection with our database. If no current user is provided,
    it will use auth_service's `get_current_user()` function to retrieve one.

    ___

    - **:param** `comment_id`: _int_: Pass the comment id to the function
    _ **:param** `db`: _Session_: Pass the database session to the function
    - **:param** `current_user`: _User_: Get the current user from the database
    :return: The comment object, but i want to return the comment_id
    """
    comment = await repository_comments.show_single_comment(comment_id, db, current_user)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.COMM_NOT_FOUND)
    return comment


@router.get("/all/{user_id}", response_model=List[CommentModel], dependencies=[Depends(allowed_get_comments)])
async def by_user_comments(user_id: int,
                           db: Session = Depends(get_db)
                           ):
    """
    The `by_user_comments function` returns all comments made by a user.\n
    **Args:**\n
    `user_id` (_int_): The id of the user whose comments are to be returned.\n
    `db` (_Session_, optional): SQLAlchemy Session. Defaults to Depends(`get_db`).\n
    `current_user` (_User_, optional): User object for the currently logged in user. Defaults to Depends(`auth_service.get_current_user`).\n
    **Returns:**\n
    _List[Comment]_: A list of Comment objects representing all comments made by a given user.\n

    ___

    - **:param** `user_id`: _int_: Specify the `user_id` of the user whose comments we want to see\n
    - **:param** `db`: _Session_: Pass the database session to the function\n
    - **:param** `current_user`: _User_: Check if the user is logged in\n
    :return: A list of comments
    """
    comments = await repository_comments.show_user_comments(user_id, db)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.COMM_NOT_FOUND)
    return comments


@router.get("/{user_id}/{photo_id}", response_model=List[CommentModel], dependencies=[Depends(allowed_get_comments)])
async def by_user_photo_comments(user_id: int,
                                photos_id: int,
                                db: Session = Depends(get_db)
                                ):
    """
    The `by_user_photo_comments function` returns all comments for a given user and photo.\n
    **Args:**\n
    `user_id` (_int_): The id of the user whose comments are being retrieved.\n
    `post_id` (_int_): The id of the post whose comments are being retrieved.\n
    **Returns:**\n
    A list containing all comment objects associated with a given user and photo.\n

    ___

    - **:param** `user_id`: _int_: Specify the `user_id` of the user whose comments we want to retrieve\n
    - **:param** `photos_id`: _int_: Get the comments for a specific photo\n
    - **:param** `db`: _Session_: Access the database\n
    - **:param** `current_user`: _User_: Get the current user who is logged in\n
    :return: A list of comments that belong to a photo
    """
    comments = await repository_comments.show_user_comments_photo(user_id, photos_id, db)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.COMM_NOT_FOUND)
    return comments
