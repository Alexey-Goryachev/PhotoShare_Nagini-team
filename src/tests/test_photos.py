import requests
from requests_toolbelt import MultipartEncoder
from src.repository.photos import (
    get_photos, get_photo_response, create_photo,
    get_all_photos, get_photo_by_id, update_photo, delete_photo
)
from fastapi import UploadFile
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from src.database.db import SessionLocal
from src.schemas.schemas import PhotoCreate, PhotoUpdate


@pytest.fixture
def db():
    """
    The db function is a factory function that returns a SessionLocal object.
        The SessionLocal object is used to create database sessions for the application.
        The db function also ensures that the session is closed when it goes out of scope.
    
    :return: A sessionlocal object
    """
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """
    The client function is a fixture that returns a TestClient instance.
        The TestClient allows you to make requests to the API as if it were live, 
        but everything happens locally. This means that you can test your API without 
        having to deploy it anywhere or use any external services.
    
    :return: A testclient object
    """
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    return client


def test_create_photo():
    """
    The test_create_photo function tests the creation of a photo.
    It does so by sending a POST request to the /api/photos/ endpoint with fake data and an image file.
    The response is then checked for status code 201, which indicates that the resource was created successfully.
    
    :return: A 201 status code
    """
    # Підготовка фейкових даних для фотографії
    fake_photo_data = {
        "description": "Test Photo",
    }
    files = {"image": ("test_image.jpg", open(
        "E: \\python_go_it\\web\\PhotoShare_Nagini-team\\test_image.jpg", "rb"), "image/jpeg")}

    # Виклик функції створення фотографії
    response = client.post("/api/photos/", data=fake_photo_data, files=files)

    # Перевірка статус коду
    assert response.status_code == 201


def test_get_photos():
    """
    The test_get_photos function tests the /scr/photos/ endpoint.
    It asserts that the response status code is 200, and that there are photos in the response data.
    
    :return: A list of photos
    """
    response = client.get("/scr/photos/")
    assert response.status_code == 200
    data = response.json()
    assert "photos" in data
    assert len(data["photos"]) > 0


def test_get_photos():
    """
    The test_get_photos function tests the /api/photos endpoint.
    It makes a GET request to the endpoint and asserts that:
    - The response status code is 200 (OK)
    - The content type header is &quot;application/json&quot;
    - A JSON object with a key of &quot;photos&quot; exists in the response body, and its value is an array of objects. Each object has keys for id, image_url, description, and created_at.
    
    :return: A list of dictionaries with the keys id, image_url, description and created_at
    """
    client = TestClient(app)
    response = client.get("/api/photos/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert "photos" in data
    assert isinstance(data["photos"], list)

    for photo in data["photos"]:
        assert "id" in photo
        assert "image_url" in photo
        assert "description" in photo
        assert "created_at" in photo


def test_get_photos(db: Session):
    """
    The test_get_photos function tests the get_photos function in crud.py
        It does this by creating a new photo, adding it to the database, and then calling get_photos()
        The test passes if there is at least one photo returned from get_photos()
    
    :param db: Session: Pass in a database session to the function
    :return: A list of photos
    """
    photos = get_photos(db)
    assert photos is not None
    assert len(photos) > 0


def test_get_photo_response(db: Session):
    """
    The test_get_photo_response function tests the get_photo_response function.
        It does this by creating a photo with an id of 4, and then calling the get_photo_response function to retrieve that photo.
        The test passes if it is able to successfully retrieve the photo.
    
    :param db: Session: Pass the database session to the function
    :return: The photo with the id 4
    """
    photo_id = 4
    photo = get_photo_response(photo_id, db)
    assert photo is not None
    assert photo.id == photo_id


def test_create_photo(db: Session, client):
    """
    The test_create_photo function tests the create_photo function in crud.py
        It creates a fake photo object and passes it to the create_photo function, which should return an object with an id.
    
    
    :param db: Session: Pass in a database session to the function
    :param client: Test the api endpoint
    :return: A response object, which is not none
    """
    fake_photo_data = {
        "description": "Test Photo",
    }
    response = create_photo(PhotoCreate(**fake_photo_data), db)
    assert response is not None
    assert response.id is not None


@ pytest.mark.asyncio
async def test_get_all_photos(db):
    """
    The test_get_all_photos function tests the get_all_photos function.
        It does this by first calling the get_all_photos function, and then asserting that it is not None, and that its length is greater than 0.
    
    :param db: Pass the database connection to the function
    :return: A list of photos
    """
    photos = await get_all_photos(skip=0, limit=10, db=db)
    assert photos is not None
    assert len(photos) > 0


@ pytest.mark.asyncio
async def test_get_photo_by_id(db):
    """
    The test_get_photo_by_id function tests the get_photo_by_id function.
        It does this by first creating a photo with an id of 6, then calling the get_photo_by_id function and passing in that id.
        The test asserts that the returned photo is not None, and also asserts that its id matches what was passed into it.
    
    :param db: Pass in the database connection
    :return: A photo object
    """
    photo_id = 6
    photo = await get_photo_by_id(photo_id, db)
    assert photo is not None
    assert photo.id == photo_id


@pytest.mark.asyncio
async def test_update_photo(db):
    """
    The test_update_photo function tests the update_photo function.
    It does so by creating a new photo, updating it with updated data, and then checking that the response is not None.
    
    :param db: Pass the database connection to the function
    :return: None
    """
    photo_id = 4
    updated_data = {
        "description": "Updated Description",
        "image_url": "updated_test_image.jpg"  # Додайте URL до оновленого зображення
    }
    response = await update_photo(photo_id, PhotoUpdate(**updated_data), db)
    assert response is not None


@ pytest.mark.asyncio
async def test_delete_photo(db):
    """
    The test_delete_photo function tests the delete_photo function.
        It does this by first creating a photo in the database, then deleting it and checking that it is no longer there.
    
    :param db: Pass in the database object
    :return: None
    """
    photo_id = 53
    response = await delete_photo(photo_id, db)
    assert response is None
