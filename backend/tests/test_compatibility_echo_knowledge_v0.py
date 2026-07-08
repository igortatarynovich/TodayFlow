"""Compatibility echo → hypothesis atom promotion."""

from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from todayflow_backend.db.models import MeaningEvent, User, UserActiveKnowledge
from todayflow_backend.services.compact_user_model_v0 import build_compact_user_model_v0
from todayflow_backend.services.compatibility_echo_knowledge_v0 import (
    COMPATIBILITY_ECHO_KNOWLEDGE_V0_CONTRACT,
    promote_compatibility_echo_knowledge_v0,
)
from todayflow_backend.services.meaning_derived_knowledge_v0 import (
    INFERRED_KNOWLEDGE_V0_CONTRACT,
    sync_meaning_derived_knowledge_v0,
)


@pytest.fixture
def echo_user(db_session: Session) -> User:
    from todayflow_backend.services.auth import hash_password

    user = User(
        email="compat_echo@test.example",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _echo_event(
    db_session: Session,
    user_id: int,
    *,
    echo: str = "yes",
    block_key: str = "conflicts",
    format_id: str = "love",
    suffix: str | None = None,
) -> MeaningEvent:
    event = MeaningEvent(
        event_id=str(uuid4())[:32],
        user_id=user_id,
        event_type="compatibility_echo",
        event_source="compatibility",
        local_date=date(2026, 7, 3),
        payload={
            "surface": "analyze_dynamics",
            "target": f"deep:{block_key}",
            "echo": echo,
            "block_key": block_key,
            "format_id": format_id,
            "scenario_id": format_id,
            "tone_mode": "serious",
        },
        idempotency_key=f"compat-echo-test-{suffix or uuid4().hex[:10]}",
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


def test_promote_echo_creates_hypothesis(db_session: Session, echo_user: User):
    event = _echo_event(db_session, echo_user.id)
    row = promote_compatibility_echo_knowledge_v0(db_session, event, commit=True)
    assert row is not None
    payload = row.payload
    assert payload.get("contract_version") == INFERRED_KNOWLEDGE_V0_CONTRACT
    assert payload.get("knowledge_type") == "hypothesis"
    assert payload.get("confirmation_required") is True
    assert payload.get("source") == COMPATIBILITY_ECHO_KNOWLEDGE_V0_CONTRACT
    assert "compat_echo_conflicts_yes" in str(payload.get("claim"))


def test_promote_echo_merges_evidence(db_session: Session, echo_user: User):
    e1 = _echo_event(db_session, echo_user.id, suffix="a")
    e2 = _echo_event(db_session, echo_user.id, suffix="b")
    promote_compatibility_echo_knowledge_v0(db_session, e1, commit=True)
    row = promote_compatibility_echo_knowledge_v0(db_session, e2, commit=True)
    assert row is not None
    assert int(row.payload.get("evidence_count") or 0) == 2
    assert len(row.payload.get("evidence_signal_ids") or []) == 2


def test_scenario_switch_promotes_interest_hypothesis(db_session: Session, echo_user: User):
    event = MeaningEvent(
        event_id=str(uuid4())[:32],
        user_id=echo_user.id,
        event_type="compatibility_scenario_switch",
        event_source="compatibility",
        local_date=date(2026, 7, 3),
        payload={
            "surface": "pair_profiles",
            "from_scenario_id": "love",
            "to_scenario_id": "office",
            "format_id": "office",
        },
        idempotency_key=f"compat-switch-{uuid4().hex[:8]}",
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    row = promote_compatibility_echo_knowledge_v0(db_session, event, commit=True)
    assert row is not None
    assert "compat_interest_office" in str(row.payload.get("claim"))


def test_aggregate_echo_pattern_sync(db_session: Session, echo_user: User):
    ref = date(2026, 7, 3)
    for i in range(3):
        db_session.add(
            MeaningEvent(
                event_id=str(uuid4())[:32],
                user_id=echo_user.id,
                event_type="compatibility_echo",
                event_source="compatibility",
                local_date=ref,
                payload={"echo": "yes", "format_id": "office", "block_key": "conflicts", "target": "deep:conflicts"},
                idempotency_key=f"compat-agg-{i}",
            )
        )
    db_session.commit()

    out = sync_meaning_derived_knowledge_v0(
        db_session, user_id=echo_user.id, reference_date=ref, window_days=28
    )
    assert out["hypotheses"] >= 1

    rows = (
        db_session.query(UserActiveKnowledge)
        .filter(UserActiveKnowledge.user_id == echo_user.id)
        .all()
    )
    claims = [
        str(r.payload.get("claim"))
        for r in rows
        if isinstance(r.payload, dict)
        and r.payload.get("contract_version") == INFERRED_KNOWLEDGE_V0_CONTRACT
    ]
    assert any("compat_reading_resonates" in c for c in claims)


def test_cum_includes_compat_hypothesis(db_session: Session, echo_user: User):
    ref = date(2026, 7, 3)
    event = _echo_event(db_session, echo_user.id)
    promote_compatibility_echo_knowledge_v0(db_session, event, commit=True)

    cum = build_compact_user_model_v0(db_session, user_id=echo_user.id, reference_date=ref)
    atoms = cum.get("knowledge_atoms_top_k") or []
    assert any(
        a.get("confirmation_required") is True and "compat_echo" in str(a.get("claim") or "")
        for a in atoms
    )
