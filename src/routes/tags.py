from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from src.conf.messages import NOT_FOUND

from src.database.db import get_db
from src.schemas import TagBase, TagResponse, TagToPhotosResponse
from src.repository import tags as repository_tags
from src.database.models import User
from src.services.roles import RoleChecker
from src.schemas import Role
from src.services.auth import auth_service

router = APIRouter(prefix='/tags', tags=["tags"])

# allowed_get_all_hashtags = RoleChecker([Role.Administrator])
# allowed_remove_hashtag = RoleChecker([Role.Administrator])
# allowed_edit_hashtag = RoleChecker([Role.Administrator])


@router.post("/new/", response_model=TagResponse)
async def create_tag(body: TagBase,
                     db: Session = Depends(get_db)
                     ):
    """
    The create_tag function creates a new tag in the database.
        The function takes a HashtagBase object as input, which is validated by pydantic.
        If the validation fails, an error message will be returned to the user.
        If it succeeds, then we create a new Tag object and add it to our database session (db).

            Args:
                body (HashtagBase): A HashtagBase object containing information about our tag that we want to create in our database. This is validated by pydantic before being passed into this function.
                db (

    :param body: HashtagBase: Define the type of data that will be passed to the function
    :param db: Session: Pass the database connection to the repository layer
    :param current_user: User: Get the user who is currently logged in
    :return: The created tag
    """
    return await repository_tags.create_tag(body, db)


# @router.get("/my/", response_model=List[TagResponse])
# async def read_my_tags(skip: int = 0,
#                        limit: int = 100,
#                        db: Session = Depends(get_db)
#                        ):
#     """
#     The read_my_tags function returns a list of tags that the current user has created.
#         The skip and limit parameters are used to paginate through the results.
#
#     :param skip: int: Skip the first n tags
#     :param limit: int: Limit the number of tags returned
#     :param db: Session: Pass the database session to the function
#     :param current_user: User: Get the user that is currently logged in
#     :return: A list of tag objects
#     """
#     tags = await repository_tags.get_my_tags(skip, limit, db)
#     return tags


@router.get("/all/", response_model=List[TagResponse])
async def read_all_tags(skip: int = 0,
                        limit: int = 100,
                        db: Session = Depends(get_db)
                        ):
    """
    The read_all_tags function returns a list of all tags in the database.
        The function takes two optional parameters: skip and limit, which are used to paginate the results.
        If no parameters are provided, then it will return up to 100 tags starting from the first tag.

    :param skip: int: Skip the first n tags in the database
    :param limit: int: Limit the number of tags returned
    :param db: Session: Get the database session
    :param current_user: User: Get the user who is currently logged in
    :return: A list of tags
    """
    tags = await repository_tags.get_all_tags(skip, limit, db)
    return tags


@router.get("/by_id/{tag_id}", response_model=TagResponse)
async def read_tag_by_id(tag_id: int,
                         db: Session = Depends(get_db)
                         ):
    """
    The read_tag_by_id function returns a single tag by its id.
        The function takes in the following parameters:
            - tag_id: int, the id of the tag to be returned.
            - db: Session = Depends(get_db), an instance of a database session object that is used for querying and updating data in our database. This parameter is optional because it has a default value (Depends(get_db)) which will be used if no other value is provided when calling this function.
            - current_user: User = Depends(auth_service.get_current_user), an instance

    :param tag_id: int: Specify the id of the tag that we want to retrieve from our database
    :param db: Session: Pass the database session to the function
    :param current_user: User: Check if the user is authenticated
    :return: A tag object
    """
    tag = await repository_tags.get_tag_by_id(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return tag


@router.put("/update_tag/{tag_id}", response_model=TagResponse)
async def update_tag(body: TagBase,
                     tag_id: int,
                     db: Session = Depends(get_db)
                     ):
    """
    The update_tag function updates a tag in the database.
        The function takes three arguments:
            - body: A HashtagBase object containing the new values for the tag.
            - tag_id: An integer representing the id of an existing hashtag to be updated.
            - db (optional): A Session object used to connect to and query a database, defaults to None if not provided by caller.
                If no session is provided, one will be created using get_db().

    :param body: HashtagBase: Pass the data from the request body to the function
    :param tag_id: int: Identify the tag to be updated
    :param db: Session: Pass the database session to the repository_tags
    :param current_user: User: Check if the user is logged in
    :return: A tag object
    """
    tag = await repository_tags.update_tag(tag_id, body, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return tag


@router.delete("/del/{tag_id}", response_model=TagResponse)
async def remove_tag(tag_id: int,
                     db: Session = Depends(get_db)
                     ):
    """
    The remove_tag function removes a tag from the database.
        Args:
            tag_id (int): The id of the tag to be removed.
            db (Session, optional): A database session object used for querying and updating data in the database. Defaults to Depends(get_db).
            current_user (User, optional): The user currently logged into this application's API endpoint. Defaults to Depends(auth_service.get_current_user).

    :param tag_id: int: Specify the id of the tag to be removed
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user's id
    :return: The tag that was removed
    """
    tag = await repository_tags.remove_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return tag


@router.post("/new/{photos_id}", response_model=TagToPhotosResponse)
async def add_tag_to_photos(photos_id: int,
                            tag_id: int,
                            db: Session = Depends(get_db)
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
    result = await repository_tags.add_tag_to_photos(photos_id, tag_id, db)
    print(result)
    return result
