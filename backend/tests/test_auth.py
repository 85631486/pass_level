import os
from pathlib import Path

TEST_DB = Path(__file__).parent / "test.db"
if TEST_DB.exists():
    TEST_DB.unlink()

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"

from app.main import create_app  # noqa: E402

app = create_app()
client = app.test_client()


def test_register_and_login_flow():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "tester@example.com",
            "phone": "1234567890",
            "nickname": "Tester",
            "password": "secret123",
        },
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == "tester@example.com"

    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "tester@example.com", "password": "secret123"},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    assert token

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "tester@example.com"

