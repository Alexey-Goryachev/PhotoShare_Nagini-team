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
from src.schemas import PhotoCreate, PhotoUpdate


@pytest.fixture
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    return client


def test_create_photo():
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
    response = client.get("/scr/photos/")
    assert response.status_code == 200
    data = response.json()
    assert "photos" in data
    assert len(data["photos"]) > 0


def test_get_photos():
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
    photos = get_photos(db)
    assert photos is not None
    assert len(photos) > 0


def test_get_photo_response(db: Session):
    photo_id = 4
    photo = get_photo_response(photo_id, db)
    assert photo is not None
    assert photo.id == photo_id


def test_create_photo(db: Session, client):
    fake_photo_data = {
        "description": "Test Photo",
    }
    response = create_photo(PhotoCreate(**fake_photo_data), db)
    assert response is not None
    assert response.id is not None


@ pytest.mark.asyncio
async def test_get_all_photos(db):
    photos = await get_all_photos(skip=0, limit=10, db=db)
    assert photos is not None
    assert len(photos) > 0


@ pytest.mark.asyncio
async def test_get_photo_by_id(db):
    photo_id = 6
    photo = await get_photo_by_id(photo_id, db)
    assert photo is not None
    assert photo.id == photo_id


@pytest.mark.asyncio
async def test_update_photo(db):
    photo_id = 4
    updated_data = {
        "description": "Updated Description",
        "image_url": "updated_test_image.jpg"  # Додайте URL до оновленого зображення
    }
    response = await update_photo(photo_id, PhotoUpdate(**updated_data), db)
    assert response is not None


@ pytest.mark.asyncio
async def test_delete_photo(db):
    photo_id = 53
    response = await delete_photo(photo_id, db)
    assert response is None
