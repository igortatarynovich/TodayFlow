"""Tests for meaning-derived knowledge (hypothesis + pattern promotion)."""

from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from todayflow_backend.db.models import MeaningEvent, User, UserActiveKnowledge
from todayflow_backend.services.compact_user_model_v0 import build_compact_user_model_v0
from todayflow_backend.services.meaning_derived_knowledge_v0 import (
    INFERRED_KNOWLEDGE_V0_CONTRACT,
    sync_meaning_derived_knowledge_v0,
)


@pytest.fixture
def pattern_user(db_session: Session) -> User:
    from todayflow_backend.services.auth import hash_password

    user = User(
        email="derived@test.example",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _mood_events(db_session: Session, user_id: int, count: int, *, start: date) -> None:
    for i in range(count):
        db_session.add(
            MeaningEvent(
                event_id=str(uuid4())[:32],
                user_id=user_id,
                event_type="mood_selected",
                event_source="today",
                local_date=start,
                payload={"mood_id": "calm"},
                idempotency_key=f"derived-mood-{i}",
            )
        )
    db_session.commit()


def test_sync_creates_hypothesis_for_three_moods(db_session: Session, pattern_user: User):
    ref = date(2026, 7, 2)
    _mood_events(db_session, pattern_user.id, 3, start=ref)

    out = sync_meaning_derived_knowledge_v0(
        db_session, user_id=pattern_user.id, reference_date=ref, window_days=28
    )
    assert out["hypotheses"] >= 1
    assert out["patterns"] == 0

    rows = (
        db_session.query(UserActiveKnowledge)
        .filter(UserActiveKnowledge.user_id == pattern_user.id)
        .all()
    )
    inferred = [
        r
        for r in rows
        if isinstance(r.payload, dict)
        and r.payload.get("contract_version") == INFERRED_KNOWLEDGE_V0_CONTRACT
    ]
    assert len(inferred) >= 1
    assert inferred[0].payload.get("knowledge_type") == "hypothesis"
    assert inferred[0].payload.get("confirmation_required") is True


def test_sync_promotes_pattern_for_seven_moods(db_session: Session, pattern_user: User):
    ref = date(2026, 7, 2)
    _mood_events(db_session, pattern_user.id, 7, start=ref)

    out = sync_meaning_derived_knowledge_v0(
        db_session, user_id=pattern_user.id, reference_date=ref, window_days=28
    )
    assert out["patterns"] >= 1

    cum = build_compact_user_model_v0(db_session, user_id=pattern_user.id, reference_date=ref)
    claims = [a.get("claim") for a in cum.get("knowledge_atoms_top_k") or [] if a.get("claim")]
    assert any("responds_to_tempo" in str(c) for c in claims) or any(
        a.get("contract_version") == "day_active_knowledge_v1"
        for a in cum.get("knowledge_atoms_top_k") or []
    )


def test_cum_includes_inferred_hypothesis(db_session: Session, pattern_user: User):
    ref = date(2026, 7, 3)
    _mood_events(db_session, pattern_user.id, 4, start=ref)
    sync_meaning_derived_knowledge_v0(
        db_session, user_id=pattern_user.id, reference_date=ref, window_days=28
    )

    cum = build_compact_user_model_v0(db_session, user_id=pattern_user.id, reference_date=ref)
    atoms = cum.get("knowledge_atoms_top_k") or []
    assert any(a.get("confirmation_required") is True for a in atoms)
