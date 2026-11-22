
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_register_user():
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
