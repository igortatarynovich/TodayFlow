"""Attachment lens hypothesis upsert + confirm promotion."""

from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from todayflow_backend.db.models import MeaningEvent, User, UserActiveKnowledge
from todayflow_backend.services.compatibility_attachment_knowledge_v0 import (
    COMPATIBILITY_ATTACHMENT_KNOWLEDGE_V0_CONTRACT,
    ensure_attachment_lens_hypotheses_v0,
    promote_compatibility_attachment_confirm_v0,
)
from todayflow_backend.services.compatibility_attachment_reference_v0 import (
    build_attachment_reference_context,
)
from todayflow_backend.services.meaning_derived_knowledge_v0 import INFERRED_KNOWLEDGE_V0_CONTRACT


@pytest.fixture
def attachment_user(db_session: Session) -> User:
    from todayflow_backend.services.auth import hash_password

    user = User(
        email="compat_attachment@test.example",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_ensure_attachment_lens_creates_hypothesis(db_session: Session, attachment_user: User):
    ctx = build_attachment_reference_context({"communication": "yes", "conflicts": "yes"})
    assert ctx is not None
    kids = ensure_attachment_lens_hypotheses_v0(
        db_session,
        user_id=attachment_user.id,
        attachment_reference=ctx,
        commit=True,
    )
    assert kids
    row = (
        db_session.query(UserActiveKnowledge)
        .filter(
            UserActiveKnowledge.user_id == attachment_user.id,
            UserActiveKnowledge.knowledge_id == kids[0],
        )
        .first()
    )
    assert row is not None
    payload = row.payload
    assert payload.get("contract_version") == INFERRED_KNOWLEDGE_V0_CONTRACT
    assert payload.get("knowledge_type") == "hypothesis"
    assert str(payload.get("claim", "")).startswith("behavior_hypothesis:attachment_lens_")
    assert payload.get("source") == COMPATIBILITY_ATTACHMENT_KNOWLEDGE_V0_CONTRACT


def test_promote_attachment_confirm_sets_verdict(db_session: Session, attachment_user: User):
    ctx = build_attachment_reference_context({"communication": "yes"})
    assert ctx is not None
    ensure_attachment_lens_hypotheses_v0(
        db_session,
        user_id=attachment_user.id,
        attachment_reference=ctx,
        commit=True,
    )
    hint = (ctx.get("attachment_style_hints") or [{}])[0]
    code = str(hint.get("code"))
    event = MeaningEvent(
        event_id=str(uuid4())[:32],
        user_id=attachment_user.id,
        event_type="compatibility_attachment_confirm",
        event_source="compatibility",
        local_date=date(2026, 7, 3),
        payload={
            "attachment_style_code": code,
            "echo": "yes",
            "verdict": "confirm",
            "label": hint.get("label"),
            "summary": hint.get("summary"),
        },
        idempotency_key=f"compat-attach-confirm-{uuid4().hex[:10]}",
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    row = promote_compatibility_attachment_confirm_v0(db_session, event, commit=True)
    assert row is not None
    payload = row.payload
    assert payload.get("user_verdict") == "confirm"
    assert payload.get("confirmation_stage") == "confirmed"
