import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src.database.models import Base
from src.database.db import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def session():
    """
    The session function is a fixture that creates a new database session for each test.
    It's useful if you have operations that are not committed at the end of the test.
    This way, you can create data in one test and use it in another, without polluting your development database with useless data.
    
    :return: A session object
    """
    # Створюємо базу даних
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def test_client(session):
    """
    The test_client function is a fixture that returns a test client for the Flask app.
    The test client allows you to make requests to your application from within tests, 
    and inspect the responses it gives back. The yield keyword means that this function 
    will return a value (the TestClient) when called, but will also execute any code after 
    the yield statement before finishing execution.
    
    :param session: Pass in the database session to the test client
    :return: A test client that can be used to make requests to the application
    """ 
    # Залежності
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture
def user_data():
    """
    The user_data function returns a dictionary containing the user's username, email address, password and roles.
    
    :return: A dictionary with the user's data
    """
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
        "roles": ["User"]
    }

@pytest.fixture
def user_data_test():
    return {
        "username": "GG@example.com",
        "email": "GG@example.com",
        "password": "Ronald80",
        "roles": ["User"],
        "is_active": True
    }