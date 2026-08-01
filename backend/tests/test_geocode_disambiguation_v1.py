"""Geocode: small towns via Nominatim; ambiguous names need explicit choice."""

from __future__ import annotations

from todayflow_backend.services import geocode as geo


def test_lookup_ambiguous_returns_need_choice(monkeypatch):
    hits = (
        {
            "name": "Alexandria",
            "local_name": "Alexandria",
            "display_name": "Alexandria, Virginia, United States",
            "country": "United States",
            "latitude": 38.8048,
            "longitude": -77.0469,
        },
        {
            "name": "Alexandria",
            "local_name": "Alexandria",
            "display_name": "Alexandria, Egypt",
            "country": "Egypt",
            "latitude": 31.2001,
            "longitude": 29.9187,
        },
    )
    monkeypatch.setattr(geo, "CITY_DATA", [])
    monkeypatch.setattr(geo, "_load_dataset", lambda: {})
    monkeypatch.setattr(geo, "_suggest_online", lambda q, limit=8: hits)
    g = geo.Geocoder()
    g.data = {}
    out = g.lookup("Alexandria")
    assert out is not None
    assert out.get("need_choice") is True
    assert len(out.get("candidates") or []) >= 2


def test_lookup_unique_small_town(monkeypatch):
    hit = {
        "name": "Slutsk",
        "local_name": "Слуцк",
        "display_name": "Слуцк, Belarus",
        "country": "Belarus",
        "latitude": 53.0274,
        "longitude": 27.5597,
        "timezone_name": "Europe/Minsk",
    }
    monkeypatch.setattr(geo, "CITY_DATA", [])
    monkeypatch.setattr(geo, "_load_dataset", lambda: {})
    monkeypatch.setattr(geo, "_suggest_online", lambda q, limit=8: (hit,))
    g = geo.Geocoder()
    g.data = {}
    out = g.lookup("Слуцк")
    assert out is not None
    assert out.get("need_choice") is not True
    assert abs(float(out["latitude"]) - 53.0274) < 0.05


def test_suggest_merges_online_even_when_offline_has_hits(monkeypatch):
    offline = {
        "name": "Berlin",
        "local_name": "Берлин",
        "country": "Germany",
        "latitude": 52.52,
        "longitude": 13.405,
    }
    online = (
        {
            "name": "Berlin",
            "local_name": "Berlin",
            "display_name": "Berlin, New Hampshire, United States",
            "country": "United States",
            "latitude": 44.4687,
            "longitude": -71.1853,
        },
    )
    monkeypatch.setattr(geo, "CITY_DATA", [offline])
    monkeypatch.setattr(geo, "_load_dataset", lambda: {geo._normalize("berlin"): offline})
    monkeypatch.setattr(geo, "_suggest_online", lambda q, limit=8: online)
    g = geo.Geocoder()
    g.data = {geo._normalize("berlin"): offline}
    rows = g.suggest("Berlin", limit=8)
    countries = {r.get("country") for r in rows}
    assert "Germany" in countries
    assert "United States" in countries
