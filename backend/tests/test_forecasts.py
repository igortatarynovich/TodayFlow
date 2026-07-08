"""Tests for Daily Forecast (Web Canon v1) API."""

import pytest
from fastapi.testclient import TestClient


def test_list_forecasts_public(client: TestClient):
    """GET /forecasts — public, no auth."""
    r = client.get("/forecasts")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


def test_list_forecasts_locale(client: TestClient):
    """GET /forecasts?locale=ru — filter by locale."""
    r = client.get("/forecasts?locale=ru")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    for f in data:
        assert f.get("locale") == "ru"


def test_list_forecasts_date_range(client: TestClient):
    """GET /forecasts?from_date=&to_date= — filter by date range."""
    r = client.get("/forecasts?locale=ru&from_date=2026-01-20&to_date=2026-01-25")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    for f in data:
        d = f.get("date")
        assert d >= "2026-01-20" and d <= "2026-01-25"


def test_get_forecast_by_date(client: TestClient):
    """GET /forecasts/by-date?date=&locale= — один прогноз."""
    r = client.get("/forecasts/by-date?date=2026-01-20&locale=ru")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data is not None
    assert data.get("date") == "2026-01-20"
    assert data.get("locale") == "ru"
    assert "blocks" in data
    assert "theme" in (data.get("blocks") or {})
    assert "markers" in data


def test_get_forecast_by_date_not_found(client: TestClient):
    """GET /forecasts/by-date — 404 при отсутствии прогноза."""
    r = client.get("/forecasts/by-date?date=2099-01-01&locale=ru")
    assert r.status_code == 404
