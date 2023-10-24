from datetime import datetime, timedelta
from typing import Optional
from unittest.mock import Mock
from jose import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette import status

from tests.conftest import test_client , user_data
import logging
from src.database import db
from src.database.db import get_db
from src.database.models import Base
from main import app
from src.schemas.schemas import UserModel, UserUpdate

logging.basicConfig(level=logging.DEBUG)

def test_signup_login_read_users_me(test_client, user_data):
    # Реєстрація нового користувача
    response_signup = test_client.post("/api/auth/signup", json=user_data)
    logging.debug(f"Response after signup: {response_signup.json()}")
    assert response_signup.status_code == 201  # Очікуємо успіх

    # Повторна реєстрація того ж самого користувача
    response = test_client.post("/api/auth/signup", json=user_data)
    assert response.status_code == status.HTTP_409_CONFLICT

    #Реєстрація з неправильним паролем
    invalid_user = user_data.copy()
    invalid_user["email"] = "invalid_email"

    response = test_client.post("/api/auth/signup", json=invalid_user)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    #Реєстрація з нерпавильною роллю
    invalid_user = user_data.copy()
    invalid_user["roles"] = ["InvalidRole"]

    response = test_client.post("/api/auth/signup", json=invalid_user)
    assert response.status_code == status.HTTP_409_CONFLICT

    result = response.json()

    # Логін з хибними даними
    invalid_login_data = {"username": user_data["email"], "password": "invalid_password"}
    response = test_client.post("/api/auth/login", json=invalid_login_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Логін користувача
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response_login = test_client.post("/api/auth/login", data=login_data)

    # Перевірка статусу відповіді
    assert response_login.status_code == status.HTTP_200_OK

    # Перевірка вмісту відповіді
    result = response_login.json()
    assert "access_token" in result
    assert result["message"] == "Logged successfully"

    # Генерація токена
    def create_access_token(data: dict, expires_delta: Optional[float] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, "secret_key", algorithm="HS256")
        return encoded_jwt

    # Додавання тесту для перевірки генерації та декодування токена
    access_token = create_access_token(data={"sub": user_data["email"], "message": "Logged successfully"})
    assert access_token is not None

    # Декодування токена
    decoded_token = jwt.decode(access_token, "secret_key", algorithms=["HS256"])
    assert decoded_token is not None
    assert decoded_token["sub"] == user_data["email"]

    if response_login.status_code != 200:
        logging.warning(f"Unexpected status code: {response_login.status_code}, Response text: {response_login.text}")
    assert response_login.status_code == 200  # Очікуємо успіх

    token = response_login.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    logging.debug(f"Response after login: {response_login.json()}")

    # Перевірка читання профілю користувача
    logging.debug("Reading user profile...")
    response_read_users_me = test_client.get("/api/users/me/", headers=headers)
    logging.debug(f"Response after reading profile: {response_read_users_me.json()}")
    assert response_read_users_me.status_code == 200
    assert response_read_users_me.json()["username"] == "testuser@example.com"

    # Логін користувача перед зміною профілю
    response_login_after_edit = test_client.post("/api/auth/login", data=login_data)
    assert response_login_after_edit.status_code == status.HTTP_200_OK

    # Отримання нового токену
    token_after_edit = response_login_after_edit.json()["access_token"]
    headers_after_edit = {"Authorization": f"Bearer {token_after_edit}"}

    # Зміна профілю користувача
    logging.debug("Editing user profile...")
    updated_data = {
        "email": "newemail@example.com",
        "username": "newemail@example.com",
        "password": "testpassword"
    }
    response_edit_user_profile = test_client.put("/api/users/edit", json=updated_data, headers=headers_after_edit)
    logging.debug(f"Response after editing profile: {response_edit_user_profile.json()}")
    assert response_edit_user_profile.status_code == 200  # Очікуємо успіх