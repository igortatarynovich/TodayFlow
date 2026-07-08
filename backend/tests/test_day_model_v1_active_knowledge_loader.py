"""A1.8 — Active Knowledge loader tests."""

from __future__ import annotations

from todayflow_backend.db import models as db_models
from todayflow_backend.services.day_model_v1_active_knowledge import (
    DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_active_knowledge_loader import (
    load_user_active_knowledge_list_v1,
    upsert_user_active_knowledge_v1,
)
from todayflow_backend.services.day_model_v1_knowledge_candidate import (
    KNOWLEDGE_TYPE_RESPONSE_STYLE,
)


def _active(**overrides):
    base = {
        "contract_version": DAY_ACTIVE_KNOWLEDGE_V1_CONTRACT,
        "knowledge_id": "know-loader-001",
        "source_knowledge_candidate_id": "kcand-loader-001",
        "knowledge_type": KNOWLEDGE_TYPE_RESPONSE_STYLE,
        "claim": "responds_to_surface:short_action",
        "confidence": 0.8,
        "evidence_count": 7,
        "evidence_window_days": 21,
        "evidence_signal_ids": [f"lsig-{i}" for i in range(7)],
        "source_pattern_id": "pat-loader-001",
        "status": "active",
        "created_at": "2026-05-31T12:00:00Z",
        "last_confirmed_at": "2026-05-31T12:00:00Z",
        "expires_at": None,
        "review_required": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "ranking_update_allowed": False,
    }
    base.update(overrides)
    return base


def test_load_returns_empty_when_no_rows(db_session):
    user = db_models.User(email="ak-loader-empty@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    assert load_user_active_knowledge_list_v1(db_session, user.id) == []


def test_upsert_and_load_active_knowledge(db_session):
    user = db_models.User(email="ak-loader-hit@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()

    upsert_user_active_knowledge_v1(
        db_session, user_id=user.id, active_knowledge=_active()
    )
    loaded = load_user_active_knowledge_list_v1(db_session, user.id)

    assert len(loaded) == 1
    assert loaded[0]["knowledge_id"] == "know-loader-001"
    assert loaded[0]["claim"] == "responds_to_surface:short_action"


def test_load_skips_invalid_payload(db_session):
    user = db_models.User(email="ak-loader-invalid@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()

    db_session.add(
        db_models.UserActiveKnowledge(
            user_id=user.id,
            knowledge_id="know-bad-001",
            status="active",
            payload={"contract_version": "wrong"},
        )
    )
    db_session.commit()

    assert load_user_active_knowledge_list_v1(db_session, user.id) == []
