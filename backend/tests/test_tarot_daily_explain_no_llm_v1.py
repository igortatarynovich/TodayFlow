"""Caller audit: GET /tarot/daily/explain must never call an LLM."""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from todayflow_backend.core.tarot_explainer import explain_tarot_card
from todayflow_backend.db import models as db_models
from todayflow_backend.services.auth import hash_password


@pytest.fixture
def user_with_birth(db_session: Session) -> db_models.User:
    user = db_models.User(
        email="tarot-read@example.com",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    db_session.add(
        db_models.UserSettings(
            user_id=user.id,
            first_name="Anna",
            locale="ru",
            gender="unspecified",
        )
    )
    db_session.add(
        db_models.AstroProfile(
            user_id=user.id,
            label="Я",
            birth_date=date(1990, 5, 15),
            time_unknown=True,
            location_name="Moscow",
            latitude=55.75,
            longitude=37.61,
            is_primary=True,
            relation="self",
        )
    )
    db_session.commit()
    return user


def test_explain_tarot_card_no_llm_on_read(
    db_session: Session, user_with_birth: db_models.User
) -> None:
    """Default read-path returns fallback without touching chat completions."""
    with patch(
        "todayflow_backend.core.tarot_explainer.chat_completion_plain",
        side_effect=AssertionError("LLM must not be called on read path"),
    ):
        out = explain_tarot_card(
            user_with_birth,
            db_session,
            card_name="The Fool",
            orientation="upright",
            target_date=date.today().isoformat(),
            card_id=0,
        )

    assert isinstance(out, dict)
    assert "meaning" in out
    assert "what_to_do" in out
    assert "what_to_avoid" in out
    assert "possible_events" in out
    assert "how_day_looks" in out
    assert "why_this_card" in out

    # First read logs a fallback; second read must hit cache and never call LLM.
    cached = explain_tarot_card(
        user_with_birth,
        db_session,
        card_name="The Fool",
        orientation="upright",
        target_date=date.today().isoformat(),
        card_id=0,
    )
    assert cached["meaning"] == out["meaning"]


@pytest.mark.smoke
def test_get_tarot_daily_explain_no_llm_on_read(
    client: TestClient, db_session: Session, user_with_birth: db_models.User
) -> None:
    """GET /tarot/daily/explain returns a deterministic explanation and never calls LLM."""
    login = client.post(
        "/auth/login",
        json={"email": user_with_birth.email, "password": "testpassword123"},
    )
    assert login.status_code == 200
    token = login.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    reveal = client.post(
        "/tarot/daily/reveal",
        headers=headers,
        json={"reveal_source": "ritual"},
    )
    assert reveal.status_code == 200
    draw = reveal.json()
    assert draw["selection_status"] == "selected"

    with patch(
        "todayflow_backend.core.tarot_explainer.chat_completion_plain",
        side_effect=AssertionError("LLM must not be called on GET /tarot/daily/explain"),
    ):
        response = client.get("/tarot/daily/explain", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["date"] == date.today().isoformat()
        assert "explanation" in data
        explanation = data["explanation"]
        assert explanation.get("meaning")
        assert "what_to_do" in explanation
        assert "what_to_avoid" in explanation
        assert "possible_events" in explanation
        assert "how_day_looks" in explanation
        assert "why_this_card" in explanation
