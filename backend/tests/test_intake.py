"""Tests for intake API endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_preview_birth_intake_complete(client: TestClient):
    """Test preview with complete birth data."""
    payload = {
        "label": "My Profile",
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "time_unknown": False,
        "timezone_name": "Europe/Moscow",
        "timezone_offset_minutes": 180,
        "location": "Moscow",
        "latitude": 55.7558,
        "longitude": 37.6173
    }
    response = client.post("/intake/preview", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "normalized_label" in data
    assert data["normalized_label"] == "My Profile"
    assert data["birth_date"] == "1990-01-01"
    assert data["birth_time"] == "12:00:00"
    assert data["time_unknown"] is False
    assert data["latitude"] == 55.7558
    assert data["longitude"] == 37.6173
    assert "warnings" in data
    assert isinstance(data["warnings"], list)


def test_preview_birth_intake_time_unknown(client: TestClient):
    """Test preview with time unknown."""
    payload = {
        "label": "Test Profile",
        "birth_date": "1990-01-01",
        "birth_time": None,
        "time_unknown": True,
        "timezone_name": "Europe/Moscow",
        "timezone_offset_minutes": 180,
        "location": "Moscow",
        "latitude": 55.7558,
        "longitude": 37.6173
    }
    response = client.post("/intake/preview", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["time_unknown"] is True
    assert data["birth_time"] is None
    assert "warnings" in data


def test_preview_birth_intake_time_missing_warning(client: TestClient):
    """Test that missing time generates a warning."""
    payload = {
        "label": "Test Profile",
        "birth_date": "1990-01-01",
        "birth_time": None,
        "time_unknown": False,  # Time is missing but not marked as unknown
        "timezone_name": "Europe/Moscow",
        "timezone_offset_minutes": 180,
        "location": "Moscow",
        "latitude": 55.7558,
        "longitude": 37.6173
    }
    response = client.post("/intake/preview", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "warnings" in data
    assert "time_missing" in data["warnings"]


def test_preview_birth_intake_label_normalization(client: TestClient):
    """Test that label is normalized (trimmed)."""
    payload = {
        "label": "  My Profile  ",  # Extra spaces
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "time_unknown": False,
        "timezone_name": "Europe/Moscow",
        "timezone_offset_minutes": 180,
        "location": "Moscow",
        "latitude": 55.7558,
        "longitude": 37.6173
    }
    response = client.post("/intake/preview", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["normalized_label"] == "My Profile"  # Should be trimmed


def test_preview_birth_intake_location_normalization(client: TestClient):
    """Test that location is normalized (trimmed)."""
    payload = {
        "label": "Test",
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "time_unknown": False,
        "timezone_name": "Europe/Moscow",
        "timezone_offset_minutes": 180,
        "location": "  Moscow  ",  # Extra spaces
        "latitude": 55.7558,
        "longitude": 37.6173
    }
    response = client.post("/intake/preview", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["location"] == "Moscow"  # Should be trimmed


def test_preview_birth_intake_invalid_date(client: TestClient):
    """Test preview with invalid date format."""
    payload = {
        "label": "Test",
        "birth_date": "invalid-date",
        "birth_time": "12:00:00",
        "time_unknown": False,
        "timezone_name": "Europe/Moscow",
        "timezone_offset_minutes": 180,
        "location": "Moscow",
        "latitude": 55.7558,
        "longitude": 37.6173
    }
    response = client.post("/intake/preview", json=payload)
    # Should return validation error
    assert response.status_code == 422


def test_preview_birth_intake_missing_required_fields(client: TestClient):
    """Test preview with missing required fields."""
    payload = {
        "label": "Test",
        # Missing birth_date
    }
    response = client.post("/intake/preview", json=payload)
    # Should return validation error
    assert response.status_code == 422

