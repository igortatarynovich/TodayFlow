"""Tests for geocoding endpoint."""

import pytest


def test_geocode_lookup(client):
    """Test geocoding lookup."""
    response = client.get("/astro/geocode?q=Moscow")
    # 200 if resolved, 404 if not found, 409 when ambiguous (no silent pick —
    # candidates are returned for an explicit choice).
    assert response.status_code in [200, 404, 409]
    if response.status_code == 200:
        data = response.json()
        assert "name" in data
        assert "latitude" in data
        assert "longitude" in data
    if response.status_code == 409:
        detail = response.json()["detail"]
        assert detail["code"] == "geocode_ambiguous"
        assert isinstance(detail["candidates"], list)


def test_geocode_lookup_empty_query(client):
    """Test geocoding with empty query."""
    response = client.get("/astro/geocode?q=")
    assert response.status_code == 422  # Validation error


def test_geocode_lookup_short_query(client):
    """Test geocoding with too short query."""
    response = client.get("/astro/geocode?q=M")
    assert response.status_code == 422  # Validation error

