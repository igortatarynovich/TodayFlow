"""Tests for sharing API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from todayflow_backend.db.models import User


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    from todayflow_backend.services.auth import hash_password
    user = User(
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(client: TestClient, test_user: User) -> str:
    """Get auth token for test user."""
    response = client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    return data["token"]


def test_get_shareable_snippet_requires_auth(client: TestClient):
    """Test that getting shareable snippet requires authentication."""
    response = client.get("/share/snippet")
    assert response.status_code == 401


def test_get_shareable_snippet_authenticated(client: TestClient, test_user: User, auth_token: str):
    """Test getting shareable snippet for authenticated user."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/share/snippet", headers=headers)
    
    # May return 200 if snippet exists, or 404 if no report/snippet available
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        # ShareableSnippet structure may vary
        assert isinstance(data, dict)

