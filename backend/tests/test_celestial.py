"""Tests for celestial API endpoints."""

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


def test_get_moon_phase_public(client: TestClient):
    """Test getting moon phase (no auth required)."""
    response = client.get("/celestial/moon-phase")
    assert response.status_code == 200
    data = response.json()
    
    assert "current" in data
    assert "next_phase" in data
    assert "upcoming" in data
    assert data["current"]["id"] is not None
    assert data["current"]["name"] is not None
    assert data["current"]["cycle_day"] is not None
    assert data["current"]["cycle_percent"] is not None


def test_get_planet_events_public(client: TestClient):
    """Test getting planet events (no auth required)."""
    response = client.get("/celestial/planet-events")
    assert response.status_code == 200
    data = response.json()
    
    assert "upcoming" in data
    assert "windows" in data
    assert isinstance(data["upcoming"], list)
    assert isinstance(data["windows"], list)


def test_get_planet_events_with_limit(client: TestClient):
    """Test getting planet events with custom limits."""
    response = client.get("/celestial/planet-events?limit=10&window_limit=3")
    assert response.status_code == 200
    data = response.json()
    
    assert "upcoming" in data
    assert "windows" in data
    assert len(data["upcoming"]) <= 10
    assert len(data["windows"]) <= 3


def test_get_planet_events_limit_validation(client: TestClient):
    """Test that limit parameters are validated."""
    # Test limit too high
    response = client.get("/celestial/planet-events?limit=100")
    assert response.status_code == 422
    
    # Test limit too low
    response = client.get("/celestial/planet-events?limit=0")
    assert response.status_code == 422
    
    # Test window_limit too high
    response = client.get("/celestial/planet-events?window_limit=10")
    assert response.status_code == 422


def test_get_check_in_requires_auth(client: TestClient):
    """Test that check-in requires authentication."""
    response = client.get("/celestial/check-in")
    assert response.status_code == 401


def test_get_check_in_authenticated(client: TestClient, test_user: User, auth_token: str):
    """Test getting check-in prompt for authenticated user."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/celestial/check-in", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert "prompt" in data
    assert "steps" in data
    assert "cta" in data
    assert isinstance(data["steps"], list)


def test_get_weekly_insight_requires_auth(client: TestClient):
    """Test that weekly insight requires authentication."""
    response = client.get("/celestial/weekly-insight")
    assert response.status_code == 401


def test_get_weekly_insight_authenticated(client: TestClient, test_user: User, auth_token: str):
    """Test getting weekly insight for authenticated user."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/celestial/weekly-insight", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert "insight" in data
    assert data["insight"]["phase_id"] is not None
    assert data["insight"]["phase_name"] is not None
    assert data["insight"]["title"] is not None
    assert data["insight"]["summary"] is not None


def test_get_transit_feed_requires_auth(client: TestClient):
    """Test that transit feed requires authentication."""
    response = client.get("/celestial/transit-feed")
    assert response.status_code == 401


def test_get_transit_feed_authenticated(client: TestClient, test_user: User, auth_token: str):
    """Test getting transit feed for authenticated user."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/celestial/transit-feed", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert "focus" in data
    assert "highlights" in data
    assert "events" in data
    assert "windows" in data
    assert isinstance(data["highlights"], list)
    assert isinstance(data["events"], list)
    assert isinstance(data["windows"], list)
    assert data["focus"]["id"] is not None
    assert data["focus"]["name"] is not None

