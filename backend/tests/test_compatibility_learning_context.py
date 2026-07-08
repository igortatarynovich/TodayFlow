"""Tests for compatibility PIM learning context."""

from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from todayflow_backend.db import models
from todayflow_backend.db.models import User
from todayflow_backend.services.auth import hash_password
from todayflow_backend.services.compatibility_learning_context import build_compatibility_learning_context


@pytest.fixture
def compat_learning_user(db_session: Session) -> User:
    user = User(
        email="compat_learning@example.com",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_build_compatibility_learning_context_empty(db_session, compat_learning_user):
    assert build_compatibility_learning_context(db_session, user_id=compat_learning_user.id) is None


def test_build_compatibility_learning_context_echoes(db_session, compat_learning_user):
    user_id = compat_learning_user.id
    db_session.add(
        models.MeaningEvent(
            event_id=str(uuid4())[:32],
            idempotency_key=f"compat-echo-{uuid4().hex[:12]}",
            user_id=user_id,
            event_type="compatibility_echo",
            event_source="compatibility",
            local_date=date.today(),
            payload={
                "echo": "yes",
                "block_key": "emotions",
                "format_id": "love",
                "target": "deep:emotions",
            },
        )
    )
    db_session.add(
        models.MeaningEvent(
            event_id=str(uuid4())[:32],
            idempotency_key=f"compat-switch-{uuid4().hex[:12]}",
            user_id=user_id,
            event_type="compatibility_scenario_switch",
            event_source="compatibility",
            local_date=date.today(),
            payload={"from_scenario_id": "love", "to_scenario_id": "office", "format_id": "office"},
        )
    )
    db_session.commit()

    ctx = build_compatibility_learning_context(db_session, user_id=user_id)
    assert ctx is not None
    assert ctx["echo_count"] == 1
    assert ctx["scenario_switches"] == 1
    assert ctx["recent_block_feedback"]["emotions"] == "yes"
    assert ctx["top_format_ids"][0]["id"] in {"love", "office"}
    assert "attachment_reference" in ctx
    assert isinstance(ctx["attachment_reference"].get("deep_block_order"), list)
