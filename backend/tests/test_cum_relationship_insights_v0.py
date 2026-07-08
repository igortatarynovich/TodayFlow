"""CUM relationship insights + ILR instance verdict."""

from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from todayflow_backend.db.models import MeaningEvent, User, UserActiveKnowledge
from todayflow_backend.services.compact_user_model_v0 import build_compact_user_model_v0
from todayflow_backend.services.compatibility_attachment_knowledge_v0 import (
    ensure_attachment_lens_hypotheses_v0,
    promote_compatibility_attachment_confirm_v0,
)
from todayflow_backend.services.compatibility_attachment_reference_v0 import (
    build_attachment_reference_context,
)
from todayflow_backend.services.interpretation_engine_v0 import (
    INTERPRETATION_INSTANCE_V0_CONTRACT,
    mark_interpretation_instance_verdict_v0,
    sync_interpretation_engine_v0,
)


@pytest.fixture
def insight_user(db_session: Session) -> User:
    from todayflow_backend.services.auth import hash_password

    user = User(
        email="cum_insight@test.example",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_cum_includes_confirmed_attachment_lens(db_session: Session, insight_user: User):
    ctx = build_attachment_reference_context({"communication": "yes", "conflicts": "yes"})
    assert ctx is not None
    ensure_attachment_lens_hypotheses_v0(
        db_session, user_id=insight_user.id, attachment_reference=ctx, commit=True
    )
    hint = (ctx.get("attachment_style_hints") or [{}])[0]
    event = MeaningEvent(
        event_id=str(uuid4())[:32],
        user_id=insight_user.id,
        event_type="compatibility_attachment_confirm",
        event_source="compatibility",
        local_date=date(2026, 7, 3),
        payload={
            "attachment_style_code": hint.get("code"),
            "echo": "yes",
            "verdict": "confirm",
        },
        idempotency_key=f"cum-insight-{uuid4().hex[:8]}",
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    promote_compatibility_attachment_confirm_v0(db_session, event, commit=True)

    cum = build_compact_user_model_v0(db_session, user_id=insight_user.id, reference_date=date(2026, 7, 3))
    insights = cum.get("relationship_insights_top_k") or []
    assert insights
    assert insights[0].get("kind") == "attachment_lens"
    assert insights[0].get("label")


def test_mark_interpretation_instance_verdict(db_session: Session, insight_user: User):
    ref = date(2026, 7, 3)
    for i in range(2):
        db_session.add(
            MeaningEvent(
                event_id=str(uuid4())[:32],
                user_id=insight_user.id,
                event_type="compatibility_echo",
                event_source="compatibility",
                local_date=ref,
                payload={"block_key": "conflicts", "echo": "yes", "format_id": "love"},
                idempotency_key=f"ilr-inst-{i}",
            )
        )
    db_session.commit()
    sync_interpretation_engine_v0(db_session, user_id=insight_user.id, reference_date=ref)

    row = (
        db_session.query(UserActiveKnowledge)
        .filter(UserActiveKnowledge.user_id == insight_user.id)
        .all()
    )
    instance = next(
        r
        for r in row
        if isinstance(r.payload, dict)
        and r.payload.get("contract_version") == INTERPRETATION_INSTANCE_V0_CONTRACT
    )
    assert mark_interpretation_instance_verdict_v0(
        db_session,
        user_id=insight_user.id,
        instance_id=instance.knowledge_id,
        verdict="confirm",
        commit=True,
    )
    payload = instance.payload
    assert payload.get("user_verdict") == "confirm"
    assert payload.get("status") == "confirmed"
