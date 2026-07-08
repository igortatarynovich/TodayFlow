"""Tests for report endpoints."""

import pytest
from todayflow_backend.db import models as db_models
from todayflow_backend.services import auth as auth_service


@pytest.fixture
def authenticated_client(client, db_session, test_user_data):
    """Create an authenticated test client."""
    # Create user
    signup_response = client.post("/auth/signup", json=test_user_data)
    token = signup_response.json()["token"]
    
    # Set authorization header
    client.headers = {"Authorization": f"Bearer {token}"}
    return client


@pytest.fixture
def sample_birth_data():
    """Sample birth data for testing."""
    return {
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "time_unknown": False,
        "latitude": 55.7558,
        "longitude": 37.6173,
        "location": "Moscow",
        "country": "Russia"
    }


def test_generate_lite_report(client, sample_birth_data):
    """Test generating a lite report."""
    response = client.post("/reports/lite", json=sample_birth_data)
    # Should work without authentication
    assert response.status_code in [200, 201]
    if response.status_code == 200:
        data = response.json()
        assert "summary" in data
        assert "sun" in data.get("summary", {})
        assert "moon" in data.get("summary", {})
        assert "rising" in data.get("summary", {})


def test_get_lite_report_unauthorized(client):
    """Test getting lite report without authentication."""
    response = client.get("/reports/lite")
    assert response.status_code == 401


def test_get_lite_report(authenticated_client, db_session, sample_birth_data):
    """Test getting lite report with authentication."""
    # First generate a report
    authenticated_client.post("/reports/lite", json=sample_birth_data)
    
    # Then get it
    response = authenticated_client.get("/reports/lite")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data


def test_generate_full_report_requires_payment(authenticated_client, sample_birth_data):
    """Test that full report requires payment."""
    response = authenticated_client.post("/reports/full", json=sample_birth_data)
    assert response.status_code == 403


def test_generate_full_report_unauthorized(client, sample_birth_data):
    """Test generating full report without authentication."""
    response = client.post("/reports/full", json=sample_birth_data)
    assert response.status_code == 401

