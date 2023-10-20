from typing import List

from sqlalchemy.orm import Session

from src.database.models import Tag, User, Photo
from src.schemas import TagBase


async def create_tag(body: TagBase,
                     db: Session,
                     user: User
                     ) -> Tag | None:
    """
    The create_tag function creates a new tag in the database.

    :param body: HashtagBase: Get the title of the hashtag from the request body
    :param user: User: Get the user id of the current user
    :param db: Session: Access the database
    :return: A hashtag object
    """
    tag = db.query(Tag).filter(Tag.title == body.title).first()
    if not tag:
        tag = Tag(
            title=body.title,
            user_id=user.id
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        return tag
    else:
        return None


async def get_my_tags(skip: int,
                      limit: int,
                      db: Session,
                      user: User) -> List[Tag]:
    """
    The get_my_tags function returns a list of Hashtag objects that are associated with the user.
    The skip and limit parameters allow for pagination.

    :param skip: int: Skip the first n tags in the database
    :param limit: int: Limit the number of results returned
    :param user: User: Get the user_id of the current user
    :param db: Session: Access the database
    :return: A list of hashtags that belong to the user
    """
    return db.query(Tag).filter(Tag.user_id == user.id).offset(skip).limit(limit).all()


async def get_all_tags(skip: int,
                       limit: int,
                       db: Session
                       ) -> List[Tag]:
    """
    The get_all_tags function returns a list of all the tags in the database.


    :param skip: int: Skip the first n tags
    :param limit: int: Limit the number of rows returned by the query
    :param db: Session: Pass in the database session
    :return: A list of hashtag objects
    """
    return db.query(Tag).offset(skip).limit(limit).all()


async def get_tag_by_id(tag_id: int,
                        db: Session
                        ) -> Tag:
    """
    The get_tag_by_id function returns a Hashtag object from the database based on its id.
        Args:
            tag_id (int): The id of the Hashtag to be returned.
            db (Session): A Session instance for interacting with the database.
        Returns:
            A single Hashtag object matching the given tag_id.

    :param tag_id: int: Specify the id of the tag we want to retrieve
    :param db: Session: Pass the database session to the function
    :return: A hashtag object
    """
    return db.query(Tag).filter(Tag.id == tag_id).first()


async def update_tag(tag_id: int,
                     body: TagBase,
                     db: Session
                     ) -> Tag | None:
    """
    The update_tag function updates a tag in the database.
        Args:
            tag_id (int): The id of the tag to update.
            body (HashtagBase): The new values for the updated tag.
            db (Session): A connection to our database session, used for querying and committing changes.

    :param tag_id: int: Identify the tag to be updated
    :param body: HashtagBase: Pass in the new title for the tag
    :param db: Session: Pass the database session to the function
    :return: A hashtag
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        tag.title = body.title
        db.commit()
    return tag


async def remove_tag(tag_id: int,
                     db: Session
                     ) -> Tag | None:
    """
    The remove_tag function removes a tag from the database.

    :param tag_id: int: Specify the id of the tag to be removed
    :param db: Session: Pass the database session to the function
    :return: A hashtag object
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        db.delete(tag)
        db.commit()
    return tag
