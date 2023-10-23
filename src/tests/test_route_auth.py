import pytest
from starlette import status
from starlette.testclient import TestClient
from src.database.models import User
from src.database.db import SessionLocal
from src.services.auth import  auth_service 
from jose import jwt


@pytest.mark.asyncio
async def test_signup(test_client: TestClient, user_data):
    """
    The test_signup function tests the signup endpoint.
    It does so by sending a POST request to /auth/signup with user_data as JSON data.
    The response is then checked for status code 201 and the presence of certain keys in its JSON body.
    
    :param test_client: TestClient: Pass in the test client that is created by pytest-asyncio
    :param user_data: Pass the data to the test_client
    :return: A response object
    """
    response = test_client.post("/auth/auth/signup", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert "user" in result
    assert "role" in result
    assert "detail" in result

@pytest.mark.asyncio
async def test_signup_invalid_email(test_client: TestClient, user_data):
    """
    The test_signup_invalid_email function tests the signup endpoint with an invalid email.
    It should return a 422 Unprocessable Entity status code and a helpful error message.
    
    :param test_client: TestClient: Make requests to the api
    :param user_data: Pass the user data to the function
    :return: A response with a status code 422 and an error message
    """
    invalid_user = user_data.copy()
    invalid_user["email"] = "invalid_email"

    response = test_client.post("/auth/auth/signup", json=invalid_user)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    result = response.json()
    # Додаткові перевірки result тут

@pytest.mark.asyncio
async def test_signup_existing_user(test_client: TestClient, user_data):
    """
    The test_signup_existing_user function tests the following:
        1. The user is not registered in the system.
        2. The user is registered in the system.
    
    :param test_client: TestClient: Make requests to the api
    :param user_data: Pass the data to the function
    :return: The following:
    """
    
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
    """
    The test_signup_invalid_role function tests the signup endpoint with an invalid role.
        It should return a 409 Conflict response.
    
    :param test_client: TestClient: Make requests to the api
    :param user_data: Pass the user data to the test function
    :return: The following:
    """
    invalid_user = user_data.copy()
    invalid_user["roles"] = ["InvalidRole"]

    response = test_client.post("/auth/auth/signup", json=invalid_user)
    assert response.status_code == status.HTTP_409_CONFLICT

    result = response.json()
    # Додаткові перевірки result тут


@pytest.mark.asyncio
async def test_login(test_client: TestClient, user_data):
    """
    The test_login function tests the login functionality of the application.
    It does so by creating a user, logging in with that user's credentials, and then verifying that an access token was returned.
    
    
    :param test_client: TestClient: Create a test client that will be used to make requests to the api
    :param user_data: Pass the data to the test function
    :return: The following error:
    """
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
    access_token = auth_service.create_access_token(data={"sub": user_data["email"], "message": "Logged successfully"})
    assert access_token is not None

    # Декодування токена
    decoded_token = jwt.decode(access_token, "secret_key", algorithms=["HS256"])
    assert decoded_token is not None
    assert decoded_token["sub"] == user_data["email"]

@pytest.mark.asyncio
async def test_login_invalid_credentials(test_client: TestClient, user_data):
    """
    The test_login_invalid_credentials function tests the login endpoint with invalid credentials.
        It should return a 401 Unauthorized response.
    
    :param test_client: TestClient: Make requests to the api
    :param user_data: Pass the user data to the test function
    :return: The following:
    """
    # Логін з хибними даними
    invalid_login_data = {"username": user_data["username"], "password": "invalid_password"}
    response = test_client.post("/auth/auth/login", data=invalid_login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    result = response.json()

