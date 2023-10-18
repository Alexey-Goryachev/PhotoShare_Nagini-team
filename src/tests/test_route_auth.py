import pytest
from starlette import status
from starlette.testclient import TestClient
from src.database.models import User
from src.database.db import SessionLocal
from src.authentication.auth import create_access_token
from jose import jwt


@pytest.mark.asyncio
async def test_signup(test_client: TestClient, user_data):
    response = test_client.post("/auth/auth/signup", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert "user" in result
    assert "role" in result
    assert "detail" in result

@pytest.mark.asyncio
async def test_signup_invalid_email(test_client: TestClient, user_data):
    invalid_user = user_data.copy()
    invalid_user["email"] = "invalid_email"

    response = test_client.post("/auth/auth/signup", json=invalid_user)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    result = response.json()
    # Додаткові перевірки result тут

@pytest.mark.asyncio
async def test_signup_existing_user(test_client: TestClient, user_data):
    response = test_client.post("/auth/auth/signup", json=user_data)
    assert response.status_code == status.HTTP_409_CONFLICT

    result = response.json()
    # Додаткові перевірки result тут

    # Реєстрація того ж користувача
    response = test_client.post("/auth/auth/signup", json=user_data)
    assert response.status_code == status.HTTP_409_CONFLICT

    result = response.json()
    # Додаткові перевірки result тут

@pytest.mark.asyncio
async def test_signup_invalid_role(test_client: TestClient, user_data):
    invalid_user = user_data.copy()
    invalid_user["roles"] = ["InvalidRole"]

    response = test_client.post("/auth/auth/signup", json=invalid_user)
    assert response.status_code == status.HTTP_409_CONFLICT

    result = response.json()
    # Додаткові перевірки result тут


@pytest.mark.asyncio
async def test_login(test_client: TestClient, user_data):
    session = SessionLocal()
    user_data["roles"] = "User"
    user = User(**user_data)
    session.add(user)
    session.commit()

    # Логін з правильними даними
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = test_client.post("/auth/auth/login", data=login_data)

    # Перевірка статусу відповіді
    assert response.status_code == status.HTTP_200_OK

    # Перевірка вмісту відповіді
    result = response.json()
    assert "access_token" in result
    assert result["message"] == "Logged successfully"

    # Закриття сесії
    session.close()

    # Додавання тесту для перевірки генерації та декодування токена
    access_token = create_access_token(data={"sub": user_data["email"], "message": "Logged successfully"})
    assert access_token is not None

    # Декодування токена
    decoded_token = jwt.decode(access_token, "secret_key", algorithms=["HS256"])
    assert decoded_token is not None
    assert decoded_token["sub"] == user_data["email"]

@pytest.mark.asyncio
async def test_login_invalid_credentials(test_client: TestClient, user_data):
    # Логін з хибними даними
    invalid_login_data = {"username": user_data["username"], "password": "invalid_password"}
    response = test_client.post("/auth/auth/login", data=invalid_login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    result = response.json()

