"""Tests for compact_user_model_v0 (UMTS-2 read path)."""

from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from todayflow_backend.db.models import MeaningEvent, User
from todayflow_backend.services.compact_user_model_v0 import (
    COMPACT_USER_MODEL_V0_CONTRACT,
    build_compact_user_model_v0,
)


@pytest.fixture
def test_user(db_session: Session) -> User:
    from todayflow_backend.services.auth import hash_password

    user = User(
        email="cum@test.example",
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
    assert response.status_code == 200
    return response.json()["token"]


def test_build_compact_user_model_empty(db_session: Session, test_user: User):
    payload = build_compact_user_model_v0(
        db_session,
        user_id=test_user.id,
        core_profile={"person": {}, "astro": {}, "numerology": {}},
        reference_date=date(2026, 7, 2),
    )
    assert payload["contract_version"] == COMPACT_USER_MODEL_V0_CONTRACT
    assert payload["current_state"]["mood_id"] is None
    assert payload["confidence"]["uncertainty_flags"]
    assert payload["recommendations"]["primary"]["id"] == "rec-today-checkin"
    assert payload["confidence"]["by_domain"]["identity"] is not None
    assert payload["confidence"]["delta_30d"] is None


def test_build_compact_user_model_identity_facts_and_promise_rec(db_session: Session, test_user: User):
    ref = date(2026, 7, 2)
    db_session.add(
        MeaningEvent(
            event_id="ev-promise",
            user_id=test_user.id,
            event_type="action_option_selected",
            event_source="today",
            event_time=datetime(2026, 7, 2, 10, 0, 0),
            local_date=ref,
            payload={"action_text": "2-min breath before work"},
            idempotency_key="k-promise",
        )
    )
    db_session.commit()

    payload = build_compact_user_model_v0(
        db_session,
        user_id=test_user.id,
        core_profile={
            "person": {
                "birth_date": "1990-02-14",
                "time_unknown": False,
                "timezone_name": "Europe/Moscow",
            },
            "astro": {},
            "numerology": {},
        },
        reference_date=ref,
    )
    assert payload["identity"]["facts"]["birth_date"] == "1990-02-14"
    assert payload["identity"]["facts"]["birth_time_known"] is True
    assert payload["recommendations"]["primary"]["id"] == "rec-day-promise"
    assert "mood_energy" not in payload["current_state"]


def test_build_compact_user_model_reads_latest_mood(db_session: Session, test_user: User):
    ref = date(2026, 7, 2)
    db_session.add(
        MeaningEvent(
            event_id="ev-mood-old",
            user_id=test_user.id,
            event_type="mood_selected",
            event_source="today",
            event_time=datetime(2026, 7, 1, 8, 0, 0),
            local_date=date(2026, 7, 1),
            payload={"mood_id": "tired"},
            idempotency_key="k-mood-old",
        )
    )
    db_session.add(
        MeaningEvent(
            event_id="ev-mood-new",
            user_id=test_user.id,
            event_type="mood_selected",
            event_source="today",
            event_time=datetime(2026, 7, 2, 9, 0, 0),
            local_date=ref,
            payload={"mood_id": "calm"},
            idempotency_key="k-mood-new",
        )
    )
    db_session.commit()

    payload = build_compact_user_model_v0(
        db_session,
        user_id=test_user.id,
        reference_date=ref,
    )
    assert payload["current_state"]["mood_id"] == "calm"
    assert payload["current_state"]["mood_captured_at"] is not None
    assert payload["current_state"]["mood_energy"]["mood_id"] == "calm"


def test_get_compact_user_model_endpoint(client: TestClient, auth_token: str):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/account/compact-user-model", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["contract_version"] == COMPACT_USER_MODEL_V0_CONTRACT
    assert "current_state" in data
    assert "knowledge_atoms_top_k" in data


def test_get_compact_user_model_requires_auth(client: TestClient):
    assert client.get("/account/compact-user-model").status_code == 401


def test_get_compact_user_model_confidence_history_endpoint(client: TestClient, auth_token: str):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/account/compact-user-model/confidence-history", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["contract_version"] == "cum_confidence_history_v0"
    assert "points" in data
    assert "summary" in data
    assert data["window_days"] == 90


def test_get_compact_user_model_confidence_history_requires_auth(client: TestClient):
    assert client.get("/account/compact-user-model/confidence-history").status_code == 401
