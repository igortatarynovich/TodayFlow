"""ILR spawn → attachment lens hypothesis."""

from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from todayflow_backend.db.models import MeaningEvent, User, UserActiveKnowledge
from todayflow_backend.services.compatibility_attachment_knowledge_v0 import (
    spawn_attachment_lens_from_ilr_v0,
)


@pytest.fixture
def spawn_user(db_session: Session) -> User:
    from todayflow_backend.services.auth import hash_password

    user = User(
        email="compat_spawn@test.example",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _echo_event(db_session: Session, user_id: int, *, block_key: str, echo: str) -> MeaningEvent:
    event = MeaningEvent(
        event_id=str(uuid4())[:32],
        user_id=user_id,
        event_type="compatibility_echo",
        event_source="compatibility",
        local_date=date(2026, 7, 3),
        payload={"block_key": block_key, "echo": echo, "format_id": "love"},
        idempotency_key=f"spawn-echo-{uuid4().hex[:8]}",
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


def test_spawn_attachment_lens_from_ilr(db_session: Session, spawn_user: User):
    events = [
        _echo_event(db_session, spawn_user.id, block_key="communication", echo="yes"),
        _echo_event(db_session, spawn_user.id, block_key="conflicts", echo="yes"),
    ]
    created = spawn_attachment_lens_from_ilr_v0(
        db_session,
        user_id=spawn_user.id,
        matching_events=events,
        interpretation_ref_id="beh.compat_echo_conflicts_yes.v1",
        evidence_count=2,
        commit=True,
    )
    assert created

    row = (
        db_session.query(UserActiveKnowledge)
        .filter(
            UserActiveKnowledge.user_id == spawn_user.id,
            UserActiveKnowledge.knowledge_id == created[0],
        )
        .one()
    )
    payload = row.payload
    assert str(payload.get("claim", "")).startswith("behavior_hypothesis:attachment_lens_")
    chain = payload.get("evidence_chain") or []
    assert chain[0].get("interpretation_ref_id") == "beh.compat_echo_conflicts_yes.v1"
