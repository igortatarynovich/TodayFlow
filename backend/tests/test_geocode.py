"""Tests for geocoding endpoint."""

import pytest


def test_geocode_lookup(client):
    """Test geocoding lookup."""
    response = client.get("/geocode/lookup?q=Moscow")
    assert response.status_code in [200, 404]  # 404 if not found, 200 if found
    if response.status_code == 200:
        data = response.json()
        assert "name" in data
        assert "latitude" in data
        assert "longitude" in data


def test_geocode_lookup_empty_query(client):
    """Test geocoding with empty query."""
    response = client.get("/geocode/lookup?q=")
    assert response.status_code == 422  # Validation error


def test_geocode_lookup_short_query(client):
    """Test geocoding with too short query."""
    response = client.get("/geocode/lookup?q=M")
    assert response.status_code == 422  # Validation error

