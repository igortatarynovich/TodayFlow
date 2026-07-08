"""Tests for reference API endpoints."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.smoke
def test_get_zodiac_signs(client: TestClient):
    """Test getting zodiac signs (no auth required)."""
    response = client.get("/reference/zodiac")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) == 12  # Should have 12 zodiac signs
    
    # Check structure of first sign
    if len(data) > 0:
        sign = data[0]
        assert "id" in sign
        assert "name" in sign
        assert "element" in sign or "modality" in sign


@pytest.mark.smoke
def test_get_planets(client: TestClient):
    """Test getting planets (no auth required)."""
    response = client.get("/reference/planets")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) > 0  # Should have planets
    
    # Check structure of first planet
    if len(data) > 0:
        planet = data[0]
        assert "id" in planet
        assert "name" in planet


def test_get_houses(client: TestClient):
    """Test getting houses (no auth required)."""
    response = client.get("/reference/houses")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) == 12  # Should have 12 houses
    
    # Check structure of first house
    if len(data) > 0:
        house = data[0]
        assert "id" in house
        assert "name" in house
        assert "description" in house
        assert "number" in house or "id" in house  # Houses should have number or identifiable id

