from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from src.conf.messages import NOT_FOUND

from src.database.db import get_db
from src.schemas import TagBase, TagResponse
from src.repository import tags as repository_tags
from src.database.models import User
from src.services.roles import RoleChecker
from src.schemas import Role
from src.authentication.auth import auth_service

router = APIRouter(prefix='/tags', tags=["tags"])

# allowed_get_all_hashtags = RoleChecker([Role.Administrator])
# allowed_remove_hashtag = RoleChecker([Role.Administrator])
# allowed_edit_hashtag = RoleChecker([Role.Administrator])


@router.post("/new/", response_model=TagResponse)
async def create_tag(body: TagBase,
                     db: Session = Depends(get_db)
                     ):
    """
    The `create_tag function` creates a new tag in the database.\n
    **The function takes a `TagBase` object as input, which is validated by pydantic.
    If the validation fails, an error message will be returned to the user.
    If it succeeds, then we create a new `Tag` object and add it to our database session (`db`).**\n

    ___

    - **:param** `body`: _TagBase_: Define the type of data that will be passed to the function
    - **:param** `db`: _Session_: Pass the database connection to the repository layer
    - **:param** `current_user`: _User_: Get the user who is currently logged in
    :return: The created tag
    """
    return await repository_tags.create_tag(body, db)


@router.get("/my/", response_model=List[TagResponse])
async def read_my_tags(skip: int = 0,
                       limit: int = 100,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)
                       ):
    """
    The `read_my_tags function` returns a list of tags that the current user has created.\n
    **The skip and limit parameters are used to paginate through the results.**\n

    ___

    - **:param** `skip`: _int_: Skip the first _n_ tags.\n
    - **:param** `limit`: _int_: Limit the number of tags returned.\n
    - **:param** `db`: _Session_: Pass the database session to the function.\n
    - **:param** `current_user`: _User_: Get the user that is currently logged in.\n
    :return: A list of tag objects
    """
    tags = await repository_tags.get_my_tags(skip, limit, db, current_user)
    return tags


@router.get("/all/", response_model=List[TagResponse])
async def read_all_tags(skip: int = 0,
                        limit: int = 100,
                        db: Session = Depends(get_db)
                        ):
    """
    The `read_all_tags function` returns a list of all tags in the database.\n
    **The function takes two optional parameters: _skip_ and _limit_, which are used to paginate the results.
    If no parameters are provided, then it will return up to 100 tags starting from the first tag.**

    ___

    - **:param** `skip`: _int_: Skip the first n tags in the database.|n
    - **:param** `limit`: _int_: Limit the number of tags returned.\n
    - **:param** `db`: _Session_: Get the database session.\n
    - **:param** `current_user`: _User_: Get the user who is currently logged in.\n
    :return: A list of tags
    """
    tags = await repository_tags.get_all_tags(skip, limit, db)
    return tags


@router.get("/by_id/{tag_id}", response_model=TagResponse)
async def read_tag_by_id(tag_id: int,
                         db: Session = Depends(get_db)
                         ):
    """
    The `read_tag_by_id function` returns a single tag by its id.\n
    **The function takes in the following parameters:\n
    - `tag_id: int`, the id of the tag to be returned.\n
    - `db: Session = Depends(get_db)`, an instance of a database session object that is used for querying and updating data in our database. This parameter is optional because it has a default value (`Depends(get_db)`) which will be used if no other value is provided when calling this function.\n
    - `current_user: User = Depends(auth_service.get_current_user)`, an instance**\n

    ___

    - **:param** `tag_id`: _int_: Specify the id of the tag that we want to retrieve from our database.\n
    - **:param** `db`: _Session_: Pass the database session to the function.\n
    - **:param** `current_user`: _User_: Check if the user is authenticated.\n
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
    The `update_tag function` updates a tag in the database.\n
    **The function takes three arguments:
    - `body`: A TagBase object containing the new values for the tag.\n
    - `tag_id`: An integer representing the id of an existing hashtag to be updated.\n
    - `db` (optional): A Session object used to connect to and query a database, defaults to None if not provided by caller.\n
    If no session is provided, one will be created using get_db().**\n

    ___

    - **:param** `body`: _TagBase_: Pass the data from the request body to the function.\n
    - **:param** `tag_id`: _int_: Identify the tag to be updated.\n
    - **:param** `db`: _Session_: Pass the database session to the `repository_tags`.\n
    - **:param** `current_user`: _User_: Check if the user is logged in.\n
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
    The `remove_tag function` removes a tag from the database.\n
    **Args:\n
    `tag_id` (_int_): The id of the tag to be removed.\n
    `db` (_Session_, optional): A database session object used for querying and updating data in the database. Defaults to `Depends(get_db)`.\n
    `current_user` (_User_, optional): The user currently logged into this application's API endpoint. Defaults to `Depends(auth_service.get_current_user)`.**\n

    ___

    - **:param** `tag_id`: _int_: Specify the id of the tag to be removed.\n
    - **:param** `db`: _Session_: Pass the database session to the function.\n
    - **:param** `current_user`: _User_: Get the current user's id.\n
    :return: The tag that was removed
    """
    tag = await repository_tags.remove_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return tag
