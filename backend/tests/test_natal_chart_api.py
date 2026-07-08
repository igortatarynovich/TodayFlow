"""Smoke и базовые проверки GET /natal-chart/ (фаза 3 приёмки)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from todayflow_backend.db.models import User


@pytest.fixture
def test_user(db_session: Session) -> User:
    from todayflow_backend.services.auth import hash_password

    user = User(
        email="natal_api@example.com",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(client: TestClient, test_user: User) -> str:
    response = client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "testpassword123"},
    )
    assert response.status_code == 200, response.text
    return str(response.json()["token"])


@pytest.mark.smoke
def test_natal_chart_requires_auth(client: TestClient):
    assert client.get("/natal-chart/").status_code == 401


@pytest.mark.smoke
def test_natal_chart_returns_positions_with_full_astro(
    client: TestClient, auth_token: str
):
    headers = {"Authorization": f"Bearer {auth_token}"}
    astro = client.post(
        "/account/astro-data",
        json={
            "label": "Я",
            "relation": "self",
            "birth_date": "1992-03-20",
            "birth_time": "09:15:00",
            "timezone_name": "UTC",
            "location_name": "Paris",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "is_primary": True,
        },
        headers=headers,
    )
    assert astro.status_code == 200, astro.text
    profile_id = astro.json()["id"]

    r = client.get("/natal-chart/?include_interpretations=true", headers=headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data.get("astro_profile_id") == profile_id
    positions = data.get("positions") or {}
    assert isinstance(positions, dict) and len(positions) > 0
    assert "sun" in positions or "Sun" in positions
    assert "cached" in data
    assert isinstance(data.get("interpretations"), dict)
