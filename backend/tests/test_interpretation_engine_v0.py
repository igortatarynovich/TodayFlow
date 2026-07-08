"""Tests for ILR interpretation engine v0."""

from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from todayflow_backend.db.models import MeaningEvent, User, UserActiveKnowledge
from todayflow_backend.services.interpretation_engine_v0 import (
    INTERPRETATION_INSTANCE_V0_CONTRACT,
    mark_inferred_knowledge_verdict_v0,
    sync_interpretation_engine_v0,
)
from todayflow_backend.services.interpretation_reference_v0 import clear_interpretation_rule_registry_cache
from todayflow_backend.data.interpretation_rule_registry_loader import clear_interpretation_rule_registry_cache as clear_registry_cache
from todayflow_backend.services.meaning_derived_knowledge_v0 import INFERRED_KNOWLEDGE_V0_CONTRACT


@pytest.fixture(autouse=True)
def _clear_ilr_caches() -> None:
    clear_interpretation_rule_registry_cache()
    clear_registry_cache()
    yield
    clear_interpretation_rule_registry_cache()
    clear_registry_cache()


@pytest.fixture
def ilr_user(db_session: Session) -> User:
    from todayflow_backend.services.auth import hash_password

    user = User(
        email="ilr@test.example",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _focus_events(db_session: Session, user_id: int, count: int, *, day: date) -> None:
    for i in range(count):
        db_session.add(
            MeaningEvent(
                event_id=str(uuid4())[:32],
                user_id=user_id,
                event_type="focus_started",
                event_source="today",
                local_date=day,
                payload={"surface": "today_ritual"},
                idempotency_key=f"ilr-focus-{i}",
            )
        )
    db_session.commit()


def test_sync_creates_instance_and_hypothesis(db_session: Session, ilr_user: User):
    ref = date(2026, 7, 2)
    _focus_events(db_session, ilr_user.id, 3, day=ref)

    out = sync_interpretation_engine_v0(
        db_session, user_id=ilr_user.id, reference_date=ref, window_days=28
    )
    assert out["instances"] >= 1
    assert out["hypotheses"] >= 1

    rows = (
        db_session.query(UserActiveKnowledge)
        .filter(UserActiveKnowledge.user_id == ilr_user.id)
        .all()
    )
    contracts = {row.payload.get("contract_version") for row in rows if isinstance(row.payload, dict)}
    assert INTERPRETATION_INSTANCE_V0_CONTRACT in contracts
    assert INFERRED_KNOWLEDGE_V0_CONTRACT in contracts

    instance = next(
        r.payload
        for r in rows
        if isinstance(r.payload, dict)
        and r.payload.get("contract_version") == INTERPRETATION_INSTANCE_V0_CONTRACT
    )
    meanings = instance.get("meanings")
    assert isinstance(meanings, list) and len(meanings) >= 2
    weight_sum = sum(float(m.get("weight") or 0) for m in meanings)
    assert abs(weight_sum - 1.0) < 0.03


def test_mark_inferred_verdict(db_session: Session, ilr_user: User):
    ref = date(2026, 7, 2)
    _focus_events(db_session, ilr_user.id, 3, day=ref)
    sync_interpretation_engine_v0(db_session, user_id=ilr_user.id, reference_date=ref)

    hypothesis = (
        db_session.query(UserActiveKnowledge)
        .filter(UserActiveKnowledge.user_id == ilr_user.id)
        .all()
    )
    kid = next(
        r.knowledge_id
        for r in hypothesis
        if isinstance(r.payload, dict)
        and r.payload.get("contract_version") == INFERRED_KNOWLEDGE_V0_CONTRACT
    )

    assert mark_inferred_knowledge_verdict_v0(
        db_session,
        user_id=ilr_user.id,
        knowledge_id=kid,
        verdict="confirm",
        commit=True,
    )

    row = (
        db_session.query(UserActiveKnowledge)
        .filter(
            UserActiveKnowledge.user_id == ilr_user.id,
            UserActiveKnowledge.knowledge_id == kid,
        )
        .one()
    )
    assert row.payload.get("user_verdict") == "confirm"


def _compat_echo_events(
    db_session: Session,
    user_id: int,
    count: int,
    *,
    day: date,
    echo: str = "yes",
    block_key: str = "conflicts",
) -> None:
    for i in range(count):
        db_session.add(
            MeaningEvent(
                event_id=str(uuid4())[:32],
                user_id=user_id,
                event_type="compatibility_echo",
                event_source="compatibility",
                local_date=day,
                payload={
                    "surface": "analyze_dynamics",
                    "target": f"deep:{block_key}",
                    "echo": echo,
                    "block_key": block_key,
                    "format_id": "love",
                },
                idempotency_key=f"ilr-compat-echo-{echo}-{i}",
            )
        )
    db_session.commit()


def test_sync_compat_echo_yes_creates_ilr_instance(db_session: Session, ilr_user: User):
    ref = date(2026, 7, 3)
    _compat_echo_events(db_session, ilr_user.id, 2, day=ref, echo="yes")

    out = sync_interpretation_engine_v0(
        db_session, user_id=ilr_user.id, reference_date=ref, window_days=28
    )
    assert out["instances"] >= 1

    rows = (
        db_session.query(UserActiveKnowledge)
        .filter(UserActiveKnowledge.user_id == ilr_user.id)
        .all()
    )
    instance = next(
        (
            r.payload
            for r in rows
            if isinstance(r.payload, dict)
            and r.payload.get("contract_version") == INTERPRETATION_INSTANCE_V0_CONTRACT
            and r.payload.get("interpretation_ref_id") == "beh.compat_echo_yes.v1"
        ),
        None,
    )
    assert instance is not None
    assert instance.get("dominant_meaning") in {
        "reading_resonates",
        "relationship_clarity",
        "conflict_awareness",
    }


def test_sync_compat_conflicts_yes_spawns_attachment_lens(db_session: Session, ilr_user: User):
    ref = date(2026, 7, 3)
    _compat_echo_events(db_session, ilr_user.id, 2, day=ref, echo="yes", block_key="conflicts")

    out = sync_interpretation_engine_v0(
        db_session, user_id=ilr_user.id, reference_date=ref, window_days=28
    )
    assert out["spawned"] >= 1

    rows = (
        db_session.query(UserActiveKnowledge)
        .filter(UserActiveKnowledge.user_id == ilr_user.id)
        .all()
    )
    lens_rows = [
        r
        for r in rows
        if isinstance(r.payload, dict)
        and str(r.payload.get("claim", "")).startswith("behavior_hypothesis:attachment_lens_")
    ]
    assert lens_rows
    chain = lens_rows[0].payload.get("evidence_chain") or []
    assert any(c.get("interpretation_ref_id") == "beh.compat_echo_conflicts_yes.v1" for c in chain if isinstance(c, dict))


def test_sync_compat_echo_yes_spawns_attachment_lens(db_session: Session, ilr_user: User):
    ref = date(2026, 7, 3)
    _compat_echo_events(db_session, ilr_user.id, 2, day=ref, echo="yes", block_key="communication")

    out = sync_interpretation_engine_v0(
        db_session, user_id=ilr_user.id, reference_date=ref, window_days=28
    )
    assert out["spawned"] >= 1

    rows = (
        db_session.query(UserActiveKnowledge)
        .filter(UserActiveKnowledge.user_id == ilr_user.id)
        .all()
    )
    lens_rows = [
        r
        for r in rows
        if isinstance(r.payload, dict)
        and str(r.payload.get("claim", "")).startswith("behavior_hypothesis:attachment_lens_")
    ]
    assert lens_rows
    chain = lens_rows[0].payload.get("evidence_chain") or []
    assert any(c.get("interpretation_ref_id") == "beh.compat_echo_yes.v1" for c in chain if isinstance(c, dict))


def test_sync_compat_conflicts_yes_requires_both_filters(db_session: Session, ilr_user: User):
    ref = date(2026, 7, 3)
    _compat_echo_events(db_session, ilr_user.id, 2, day=ref, echo="no", block_key="conflicts")

    out = sync_interpretation_engine_v0(
        db_session, user_id=ilr_user.id, reference_date=ref, window_days=28
    )
    rows = (
        db_session.query(UserActiveKnowledge)
        .filter(UserActiveKnowledge.user_id == ilr_user.id)
        .all()
    )
    conflict_yes = [
        r.payload
        for r in rows
        if isinstance(r.payload, dict)
        and r.payload.get("interpretation_ref_id") == "beh.compat_echo_conflicts_yes.v1"
    ]
    assert conflict_yes == []
    assert out["instances"] >= 1
