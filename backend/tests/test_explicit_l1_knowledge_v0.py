"""Tests for explicit L1 knowledge promotion (UKM write path v0)."""

from datetime import date, datetime

import pytest
from sqlalchemy.orm import Session

from todayflow_backend.db.models import MeaningEvent, User, UserActiveKnowledge
from todayflow_backend.services.explicit_l1_knowledge_v0 import (
    EXPLICIT_L1_KNOWLEDGE_V0_CONTRACT,
    load_user_explicit_l1_knowledge_v0,
    promote_meaning_event_explicit_l1_v0,
)


@pytest.fixture
def test_user(db_session: Session) -> User:
    from todayflow_backend.services.auth import hash_password

    user = User(
        email="el1@test.example",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(client, test_user: User) -> str:
    from fastapi.testclient import TestClient

    response = client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "testpassword123"},
    )
    assert response.status_code == 200
    return response.json()["token"]


def _mood_event(user_id: int) -> MeaningEvent:
    return MeaningEvent(
        event_id="ev-el1-mood",
        user_id=user_id,
        event_type="mood_selected",
        event_source="today",
        event_time=datetime(2026, 7, 2, 10, 0, 0),
        local_date=date(2026, 7, 2),
        payload={"mood_id": "calm"},
        idempotency_key="el1-mood-key",
    )


def test_promote_mood_creates_explicit_l1_atom(db_session: Session, test_user: User):
    event = _mood_event(test_user.id)
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    row = promote_meaning_event_explicit_l1_v0(db_session, event, commit=True)
    assert row is not None
    assert row.payload["contract_version"] == EXPLICIT_L1_KNOWLEDGE_V0_CONTRACT
    assert row.payload["claim"] == "explicit_mood:calm"
    assert row.payload["knowledge_type"] == "fact"

    loaded = load_user_explicit_l1_knowledge_v0(db_session, test_user.id)
    assert len(loaded) == 1
    assert loaded[0]["value"] == "calm"


def test_promote_mood_updates_same_knowledge_id(db_session: Session, test_user: User):
    event1 = _mood_event(test_user.id)
    db_session.add(event1)
    db_session.commit()
    db_session.refresh(event1)
    promote_meaning_event_explicit_l1_v0(db_session, event1, commit=True)

    event2 = MeaningEvent(
        event_id="ev-el1-mood-2",
        user_id=test_user.id,
        event_type="mood_selected",
        event_source="today",
        event_time=datetime(2026, 7, 2, 18, 0, 0),
        local_date=date(2026, 7, 2),
        payload={"mood_id": "tired"},
        idempotency_key="el1-mood-key-2",
    )
    db_session.add(event2)
    db_session.commit()
    db_session.refresh(event2)
    promote_meaning_event_explicit_l1_v0(db_session, event2, commit=True)

    rows = (
        db_session.query(UserActiveKnowledge)
        .filter(UserActiveKnowledge.user_id == test_user.id)
        .all()
    )
    el1_rows = [
        r
        for r in rows
        if isinstance(r.payload, dict)
        and r.payload.get("contract_version") == EXPLICIT_L1_KNOWLEDGE_V0_CONTRACT
    ]
    assert len(el1_rows) == 1
    assert el1_rows[0].payload["claim"] == "explicit_mood:tired"


def test_meaning_events_endpoint_promotes_explicit_l1(client, test_user, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post(
        "/meaning/events",
        headers=headers,
        json={
            "events": [
                {
                    "event_type": "head_topic_selected",
                    "event_source": "today",
                    "local_date": "2026-07-02",
                    "payload": {"topic_id": "work"},
                    "idempotency_key": "promote-focus-1",
                }
            ]
        },
    )
    assert response.status_code == 200
    assert response.json()["accepted"] == 1

    cum = client.get("/account/compact-user-model", headers=headers)
    assert cum.status_code == 200
    atoms = cum.json().get("knowledge_atoms_top_k") or []
    assert any(a.get("claim") == "explicit_focus:work" for a in atoms)


def test_promote_interpretation_confirm(db_session: Session, test_user: User):
    event = MeaningEvent(
        event_id="ev-confirm-tarot",
        user_id=test_user.id,
        event_type="sphere_feedback",
        event_source="today",
        event_time=datetime(2026, 7, 2, 11, 0, 0),
        local_date=date(2026, 7, 2),
        payload={
            "interpretation_confirm": True,
            "target": "tarot_impact",
            "echo": "yes",
        },
        idempotency_key="confirm-tarot-1",
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    row = promote_meaning_event_explicit_l1_v0(db_session, event, commit=True)
    assert row is not None
    assert row.payload["claim"] == "interpretation_confirm:tarot_impact_yes"


def test_promote_profile_atom_correction(db_session: Session, test_user: User):
    event = MeaningEvent(
        event_id="ev-profile-corr",
        user_id=test_user.id,
        event_type="profile_atom_correction",
        event_source="profile",
        event_time=datetime(2026, 7, 2, 12, 0, 0),
        local_date=date(2026, 7, 2),
        payload={
            "knowledge_id": "el1-mood-current",
            "correction": "reject",
            "claim_summary": "Состояние: calm",
        },
        idempotency_key="profile-corr-1",
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    row = promote_meaning_event_explicit_l1_v0(db_session, event, commit=True)
    assert row is not None
    assert row.payload.get("user_verdict") == "reject"
    assert row.payload.get("source_knowledge_id") == "el1-mood-current"
