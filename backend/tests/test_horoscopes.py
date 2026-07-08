"""Tests for horoscopes API endpoints."""

import pytest
from datetime import date
from fastapi.testclient import TestClient


def test_get_all_horoscopes_basic(client: TestClient):
    """Test getting all horoscopes with basic birth date."""
    response = client.post(
        "/horoscopes/all",
        json={
            "birth_date": "1990-01-01"
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "chinese" in data
    assert "zoroastrian" in data
    assert "tibetan" in data
    
    # Check structure of each horoscope
    assert "sign" in data["chinese"]
    assert "sign" in data["zoroastrian"]
    assert "sign" in data["tibetan"]


def test_get_all_horoscopes_with_astrology(client: TestClient):
    """Test getting all horoscopes including Western astrology."""
    response = client.post(
        "/horoscopes/all",
        json={
            "birth_date": "1990-01-01",
            "birth_time": "12:00",
            "latitude": 55.7558,
            "longitude": 37.6173
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "chinese" in data
    assert "zoroastrian" in data
    assert "tibetan" in data
    # Astrology is optional and might not always be present
    # (depends on service availability)


def test_get_all_horoscopes_with_numerology(client: TestClient):
    """Test getting all horoscopes including numerology."""
    response = client.post(
        "/horoscopes/all",
        json={
            "birth_date": "1990-01-01",
            "full_name": "John Doe"
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "chinese" in data
    assert "zoroastrian" in data
    assert "tibetan" in data
    # Numerology is optional
    if "numerology" in data:
        assert "life_path" in data["numerology"]
        assert "expression" in data["numerology"]


def test_get_all_horoscopes_complete(client: TestClient):
    """Test getting all horoscopes with all optional fields."""
    response = client.post(
        "/horoscopes/all",
        json={
            "birth_date": "1990-01-01",
            "birth_time": "12:00",
            "latitude": 55.7558,
            "longitude": 37.6173,
            "full_name": "John Doe"
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "chinese" in data
    assert "zoroastrian" in data
    assert "tibetan" in data


def test_get_all_horoscopes_invalid_date(client: TestClient):
    """Test getting horoscopes with invalid date format."""
    response = client.post(
        "/horoscopes/all",
        json={
            "birth_date": "invalid-date"
        }
    )
    # Should return validation error
    assert response.status_code == 422


def test_get_all_horoscopes_missing_date(client: TestClient):
    """Test getting horoscopes without required birth_date."""
    response = client.post(
        "/horoscopes/all",
        json={}
    )
    # Should return validation error
    assert response.status_code == 422

