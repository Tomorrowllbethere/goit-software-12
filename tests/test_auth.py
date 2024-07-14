import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from main import app
from str.database.models import Base
from str.database.db import get_db
from fastapi_limiter import FastAPILimiter
from str.conf.config import settings
from redis import asyncio as aioredis


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
async def lifespan():
    """Initialize the Redis connection and FastAPI limiter on startup."""
    redis = aioredis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis)


@pytest.fixture(scope="module")
def session(lifespan):
    """Create the database session."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(session):
    """Test client with overridden dependencies."""
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    """Sample user data for testing."""
    return {"username": "deadpool", "email": "deadpool@example.com", "password": "123456789"}


@patch('fastapi_limiter.FastAPILimiter')
@pytest.mark.asyncio
async def test_create_user(mock_limiter, client, user):
    """Test case for user creation."""
    # Mock FastAPILimiter.init
    mock_init = MagicMock()
    mock_limiter.init.return_value = mock_init

    # Set up mock_send_email
    mock_send_email = MagicMock()
    with patch('str.routes.auth.send_email', mock_send_email):
        response = await client.post("/api/auth/signup", json=user)

    # Perform assertions based on the response
    assert response.status_code == 201
    assert "user" in response.json()
    assert response.json()["user"]["username"] == user["username"]
    assert response.json()["detail"] == "User successfully created. Check your email for confirmation."

    # Check that FastAPILimiter.init was called once
    mock_limiter.init.assert_called_once()

    # Optionally, you can assert other mock behaviors or interactions here

'''
pytest tests/test_auth.py -v

'''