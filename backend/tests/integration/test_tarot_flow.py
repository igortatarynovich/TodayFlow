"""Integration tests for tarot flow."""

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
    """Bearer token from POST /auth/login (`token` field)."""
    response = client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "testpassword123"},
    )
    assert response.status_code == 200
    data = response.json()
    return data["token"]


def test_tarot_daily_draw_flow(client: TestClient, test_user: User, auth_token: str):
    """Daily draw и структура /tarot/history (избранное см. unit tests/test_tarot.py — там же БД что и SessionLocal)."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    daily_response = client.get("/tarot/daily", headers=headers)
    assert daily_response.status_code == 200
    daily_data = daily_response.json()
    assert "card" in daily_data
    assert "date" in daily_data

    history_response = client.get("/tarot/history", headers=headers)
    assert history_response.status_code == 200
    history_data = history_response.json()
    assert "today" in history_data
    assert "history" in history_data
    assert isinstance(history_data["history"], list)
    assert "streak_days" in history_data


def test_tarot_spread_flow(client: TestClient, test_user: User, auth_token: str):
    """POST /tarot/spread с spread_id → GET /tarot/spread/history."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Идентификатор из DATA/astrology_reference/tarot_spreads.json (три позиции).
    # Продуктовый алиас three_cards на вебе маппится в шаблоны отдельно; API принимает id из справочника.
    spread_response = client.post(
        "/tarot/spread",
        json={"spread_id": "clarity_triad"},
        headers=headers,
    )
    assert spread_response.status_code == 200
    spread_data = spread_response.json()
    assert spread_data.get("spread_id") == "clarity_triad"
    assert "cards" in spread_data
    assert len(spread_data["cards"]) == 3

    history_response = client.get("/tarot/spread/history", headers=headers)
    assert history_response.status_code == 200
    history_data = history_response.json()
    assert "history" in history_data
    assert isinstance(history_data["history"], list)
    assert len(history_data["history"]) >= 1


def test_tarot_daily_deterministic(client: TestClient, test_user: User, auth_token: str):
    """Same date → same card."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    first_response = client.get("/tarot/daily", headers=headers)
    assert first_response.status_code == 200
    first_data = first_response.json()

    second_response = client.get("/tarot/daily", headers=headers)
    assert second_response.status_code == 200
    second_data = second_response.json()

    assert first_data["date"] == second_data["date"]
    assert first_data["card"]["id"] == second_data["card"]["id"]
