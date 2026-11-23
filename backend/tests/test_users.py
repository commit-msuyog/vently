import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.config import settings
from app.db.session import Base
from app.db.dependencies import get_db

from sqlalchemy.engine import make_url

from app.core.security import verify_password
from app.models.user import User


TEST_DATABASE_URL = make_url(settings.database_url).set(database="vently_test")

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_register_user(client):
    response = client.post(
        "/api/v1/users/register",
        json={
            "full_name": "Test User",
            "email": "testuser@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["full_name"] == "Test User"
    assert data["email"] == "testuser@example.com"
    assert "password" not in data
    assert "password_hash" not in data

def test_register_duplicate_email(client):
    user_data = {
        "full_name": "Test User",
        "email": "duplicate@example.com",
        "password": "TestPassword123!",
    }

    first_response = client.post("/api/v1/users/register", json=user_data)
    second_response = client.post("/api/v1/users/register", json=user_data)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email is already registered"

@pytest.mark.parametrize(
    "user_data",
    [
        {
            "full_name": "Test User",
            "email": "not-an-email",
            "password": "TestPassword123!",
        },
        {
            "full_name": "Test User",
            "email": "invalidpassword@example.com",
            "password": "short",
        },
        {
            "full_name": "A",
            "email": "invalidname@example.com",
            "password": "TestPassword123!",
        },
    ],
)
def test_register_invalid_data(client, user_data):
    response = client.post("/api/v1/users/register", json=user_data)

    assert response.status_code == 422

def test_password_is_hashed(client):
    password = "TestPassword123!"

    response = client.post(
        "/api/v1/users/register",
        json={
            "full_name": "Hash Test",
            "email": "hashtest@example.com",
            "password": password,
        },
    )

    assert response.status_code == 201

    user_id = response.json()["id"]

    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()

        assert user is not None
        assert user.password_hash != password
        assert verify_password(password, user.password_hash)
    finally:
        db.close()