"""POST /meaning/events — канонические типы событий (Day Engine DE-4)."""

import pytest
from sqlalchemy.orm import Session

from todayflow_backend.db.models import User
from todayflow_backend.services.auth import hash_password


@pytest.fixture
def meaning_events_user(db_session: Session) -> User:
    user = User(
        email="meaning_events@example.com",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def meaning_events_auth_headers(client, meaning_events_user):
    signup_data = {"email": meaning_events_user.email, "password": "testpassword123"}
    client.post("/auth/signup", json=signup_data)
    response = client.post("/auth/login", json=signup_data)
    assert response.status_code == 200, response.text
    token = response.json().get("token")
    assert token
    return {"Authorization": f"Bearer {token}"}


def test_post_meaning_events_accepts_canonical_today_types(
    client, meaning_events_auth_headers
) -> None:
    body = {
        "events": [
            {
                "event_type": "sphere_opened",
                "event_source": "today",
                "quality_score": 0.8,
                "payload": {"sphere_id": "mind"},
                "idempotency_key": "pytest-sphere-opened-1",
            }
        ]
    }
    r = client.post("/meaning/events", json=body, headers=meaning_events_auth_headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["accepted"] == 1
    assert data["deduplicated"] == 0
    assert data["total"] == 1


def test_post_meaning_events_accepts_today_day_history_first_visible(
    client, meaning_events_auth_headers
) -> None:
    body = {
        "events": [
            {
                "event_type": "today_day_history_first_visible",
                "event_source": "today",
                "quality_score": 0.45,
                "payload": {"surface": "your_day_spheres", "generation_id": 7},
                "idempotency_key": "pytest-day-history-visible-1",
            }
        ]
    }
    r = client.post("/meaning/events", json=body, headers=meaning_events_auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["accepted"] == 1


def test_post_meaning_events_accepts_today_guide_why_opened(
    client, meaning_events_auth_headers
) -> None:
    body = {
        "events": [
            {
                "event_type": "today_guide_why_opened",
                "event_source": "today",
                "quality_score": 0.55,
                "payload": {"surface": "ritual_day_summary", "generation_id": 42},
                "idempotency_key": "pytest-guide-why-1",
            }
        ]
    }
    r = client.post("/meaning/events", json=body, headers=meaning_events_auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["accepted"] == 1


def test_post_meaning_events_accepts_narrative_depth_changed(
    client, meaning_events_auth_headers
) -> None:
    body = {
        "events": [
            {
                "event_type": "today_narrative_depth_changed",
                "event_source": "today",
                "quality_score": 0.55,
                "payload": {"depth_level": "quick", "source": "today_page"},
                "idempotency_key": "pytest-narrative-depth-1",
            }
        ]
    }
    r = client.post("/meaning/events", json=body, headers=meaning_events_auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["accepted"] == 1


def test_post_meaning_events_accepts_onboarding_intent_selected(
    client, meaning_events_auth_headers
) -> None:
    body = {
        "events": [
            {
                "event_type": "onboarding_intent_selected",
                "event_source": "onboarding",
                "payload": {"theme": "focus", "day_key": "2026-06-23"},
                "idempotency_key": "pytest-onboarding-intent-1",
            }
        ]
    }
    r = client.post("/meaning/events", json=body, headers=meaning_events_auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["accepted"] == 1


def test_post_meaning_events_rejects_unknown_type(client, meaning_events_auth_headers) -> None:
    body = {
        "events": [
            {
                "event_type": "not_a_real_event_type",
                "event_source": "today",
                "idempotency_key": "pytest-unknown-1",
            }
        ]
    }
    r = client.post("/meaning/events", json=body, headers=meaning_events_auth_headers)
    assert r.status_code == 400


def test_post_meaning_events_deduplicates_against_existing_db(client, meaning_events_auth_headers) -> None:
    key = "pytest-batch-db-dedup-1"
    first = {
        "events": [
            {
                "event_type": "day_opened",
                "event_source": "today",
                "idempotency_key": key,
            }
        ]
    }
    r1 = client.post("/meaning/events", json=first, headers=meaning_events_auth_headers)
    assert r1.status_code == 200, r1.text
    assert r1.json()["accepted"] == 1

    second = {
        "events": [
            {
                "event_type": "day_opened",
                "event_source": "today",
                "idempotency_key": key,
            },
            {
                "event_type": "day_opened",
                "event_source": "today",
                "idempotency_key": key,
            },
        ]
    }
    r2 = client.post("/meaning/events", json=second, headers=meaning_events_auth_headers)
    assert r2.status_code == 200, r2.text
    data = r2.json()
    assert data["accepted"] == 0
    assert data["deduplicated"] == 2


def test_post_meaning_events_deduplicates_within_batch(client, meaning_events_auth_headers) -> None:
    """Outbox flush can send the same idempotency_key twice in one batch — must not 500."""
    key = "pytest-batch-dedup-1"
    body = {
        "events": [
            {
                "event_type": "day_opened",
                "event_source": "today",
                "idempotency_key": key,
                "event_time": "2026-07-02T12:00:00.000Z",
            },
            {
                "event_type": "day_opened",
                "event_source": "today",
                "idempotency_key": key,
                "event_time": "2026-07-02T12:01:00.000Z",
            },
        ]
    }
    r = client.post("/meaning/events", json=body, headers=meaning_events_auth_headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["accepted"] == 1
    assert data["deduplicated"] == 1
    assert data["total"] == 2


def test_post_meaning_events_accepts_tarot_question_flow_types(
    client, meaning_events_auth_headers
) -> None:
    body = {
        "events": [
            {
                "event_type": "tarot_session_started",
                "event_source": "flow",
                "idempotency_key": "pytest-tarot-flow-1",
                "payload": {"session_id": "s1", "surface": "tarot_hub"},
            },
            {
                "event_type": "tarot_question_domain_selected",
                "event_source": "flow",
                "idempotency_key": "pytest-tarot-flow-2",
                "payload": {"session_id": "s1", "concern_domain": "work"},
            },
            {
                "event_type": "tarot_question_refined",
                "event_source": "flow",
                "idempotency_key": "pytest-tarot-flow-3",
                "payload": {"session_id": "s1", "refinement_id": "stay_or_leave"},
            },
            {
                "event_type": "tarot_spread_selected",
                "event_source": "flow",
                "idempotency_key": "pytest-tarot-flow-4",
                "payload": {"session_id": "s1", "spread_id": "three_cards"},
            },
            {
                "event_type": "tarot_question_submitted",
                "event_source": "flow",
                "idempotency_key": "pytest-tarot-flow-5",
                "payload": {"session_id": "s1", "question_text": "Стоит ли менять работу?"},
            },
            {
                "event_type": "tarot_reading_resonance",
                "event_source": "flow",
                "idempotency_key": "pytest-tarot-flow-6",
                "payload": {"resonance": "partial", "spread_id": "three_cards"},
            },
            {
                "event_type": "tarot_deepen_started",
                "event_source": "flow",
                "idempotency_key": "pytest-tarot-flow-7",
                "payload": {
                    "source": "today",
                    "card_id": 8,
                    "orientation": "upright",
                    "spread_id": "three_cards",
                },
            },
        ]
    }
    r = client.post("/meaning/events", json=body, headers=meaning_events_auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["accepted"] == 7


def test_post_meaning_events_accepts_compatibility_attachment_confirm(
    client, meaning_events_auth_headers
) -> None:
    body = {
        "events": [
            {
                "event_type": "compatibility_attachment_confirm",
                "event_source": "compatibility",
                "quality_score": 0.9,
                "payload": {
                    "surface": "analyze_dynamics",
                    "attachment_style_code": "anxious",
                    "label": "Тревожный",
                    "summary": "Может быть важно прояснять ожидания.",
                    "echo": "yes",
                    "verdict": "confirm",
                    "knowledge_id": "inf-attachment-lens-anxious",
                },
                "idempotency_key": "pytest-attachment-confirm-1",
            }
        ]
    }
    r = client.post("/meaning/events", json=body, headers=meaning_events_auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["accepted"] == 1


def test_post_meaning_events_accepts_interpretation_instance_confirm(
    client, meaning_events_auth_headers
) -> None:
    body = {
        "events": [
            {
                "event_type": "interpretation_instance_confirm",
                "event_source": "profile",
                "quality_score": 0.9,
                "payload": {
                    "surface": "profile_quick_map",
                    "instance_id": "pytest-ilr-inst-1",
                    "interpretation_ref_id": "beh.compat_echo_yes.v1",
                    "correction": "partial",
                    "verdict": "partial",
                    "summary": "Частично откликается.",
                },
                "idempotency_key": "pytest-ilr-confirm-1",
            }
        ]
    }
    r = client.post("/meaning/events", json=body, headers=meaning_events_auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["accepted"] == 1
