"""Tests for numerology API endpoints."""

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


def test_compute_name_profile_public(client: TestClient):
    """Test computing numerology profile without authentication."""
    response = client.post(
        "/numerology/name",
        json={
            "full_name": "John Doe",
            "birth_date": "1990-01-01"
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "life_path" in data
    assert "expression" in data
    assert "soul_urge" in data
    assert "personality" in data
    assert data["life_path"]["number"] is not None


def test_compute_name_profile_authenticated(client: TestClient, test_user: User, auth_token: str):
    """Test computing numerology profile with authentication (saves to profile)."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post(
        "/numerology/name",
        json={
            "full_name": "Jane Smith",
            "birth_date": "1995-05-15"
        },
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "life_path" in data
    assert "expression" in data
    assert "soul_urge" in data
    assert "personality" in data


def test_compute_name_profile_invalid_date(client: TestClient):
    """Test computing profile with invalid date format."""
    response = client.post(
        "/numerology/name",
        json={
            "full_name": "Test User",
            "birth_date": "invalid-date"
        }
    )
    # Should return 400 or 422 depending on validation
    assert response.status_code in [400, 422]


def test_compute_name_profile_empty_name(client: TestClient):
    """Test computing profile with empty name."""
    response = client.post(
        "/numerology/name",
        json={
            "full_name": "",
            "birth_date": "1990-01-01"
        }
    )
    # Should return validation error
    assert response.status_code in [400, 422]


def test_numerology_daily_public(client: TestClient):
    """Test getting daily numerology insight (no auth required)."""
    response = client.get("/numerology/daily")
    assert response.status_code == 200
    data = response.json()
    
    assert "number" in data
    assert "description" in data
    assert data["number"] is not None


def test_numerology_history_requires_auth(client: TestClient):
    """Test that numerology history requires authentication."""
    response = client.get("/numerology/history")
    assert response.status_code == 401


def test_numerology_history_empty(client: TestClient, test_user: User, auth_token: str):
    """Test getting empty numerology history."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/numerology/history", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) == 0


def test_numerology_history_with_profiles(client: TestClient, test_user: User, auth_token: str):
    """Test getting numerology history with saved profiles."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # First, compute and save a profile
    response = client.post(
        "/numerology/name",
        json={
            "full_name": "Test User",
            "birth_date": "1990-01-01"
        },
        headers=headers
    )
    assert response.status_code == 200
    
    # Then get history
    response = client.get("/numerology/history", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "life_path" in data[0]
    assert "expression" in data[0]

