"""Tests for cum_confidence_history_v0 (delta_30d store)."""

from datetime import date, timedelta

import pytest
from sqlalchemy.orm import Session

from todayflow_backend.db.models import CumConfidenceSnapshot, User
from todayflow_backend.services.compact_user_model_v0 import build_compact_user_model_v0
from todayflow_backend.services.cum_confidence_history_v0 import (
    apply_confidence_delta_30d,
    compute_delta_30d,
    find_baseline_snapshot_for_delta_30d,
    load_cum_confidence_history_v0,
    upsert_cum_confidence_snapshot,
)


@pytest.fixture
def history_user(db_session: Session) -> User:
    from todayflow_backend.services.auth import hash_password

    user = User(
        email="cum-history@test.example",
        password_hash=hash_password("testpassword123"),
        is_paid=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_compute_delta_30d_rounds():
    assert compute_delta_30d(0.65, 0.5) == 0.15
    assert compute_delta_30d(0.4, 0.55) == -0.15


def test_upsert_snapshot_idempotent(db_session: Session, history_user: User):
    ref = date(2026, 7, 2)
    confidence = {
        "overall": 0.45,
        "by_domain": {"identity": 0.5},
        "meaning_events_28d": 3,
    }
    upsert_cum_confidence_snapshot(
        db_session, user_id=history_user.id, snapshot_date=ref, confidence=confidence, commit=True
    )
    upsert_cum_confidence_snapshot(
        db_session,
        user_id=history_user.id,
        snapshot_date=ref,
        confidence={**confidence, "overall": 0.6},
        commit=True,
    )
    rows = (
        db_session.query(CumConfidenceSnapshot)
        .filter(CumConfidenceSnapshot.user_id == history_user.id)
        .all()
    )
    assert len(rows) == 1
    assert rows[0].overall == 0.6


def test_delta_30d_null_without_baseline(db_session: Session, history_user: User):
    ref = date(2026, 7, 2)
    enriched = apply_confidence_delta_30d(
        db_session,
        user_id=history_user.id,
        reference_date=ref,
        confidence={"overall": 0.55, "by_domain": {}, "meaning_events_28d": 0},
        commit_snapshot=True,
    )
    assert enriched["delta_30d"] is None


def test_delta_30d_from_baseline_30_days_ago(db_session: Session, history_user: User):
    ref = date(2026, 7, 2)
    baseline_date = ref - timedelta(days=30)
    db_session.add(
        CumConfidenceSnapshot(
            user_id=history_user.id,
            snapshot_date=baseline_date,
            overall=0.4,
            by_domain={"identity": 0.35},
            meaning_events_28d=5,
        )
    )
    db_session.commit()

    baseline = find_baseline_snapshot_for_delta_30d(
        db_session, user_id=history_user.id, reference_date=ref
    )
    assert baseline is not None
    assert baseline.snapshot_date == baseline_date

    enriched = apply_confidence_delta_30d(
        db_session,
        user_id=history_user.id,
        reference_date=ref,
        confidence={"overall": 0.55, "by_domain": {}, "meaning_events_28d": 10},
        commit_snapshot=True,
    )
    assert enriched["delta_30d"] == 0.15


def test_delta_30d_ignored_when_baseline_too_old(db_session: Session, history_user: User):
    ref = date(2026, 7, 2)
    db_session.add(
        CumConfidenceSnapshot(
            user_id=history_user.id,
            snapshot_date=ref - timedelta(days=60),
            overall=0.3,
            by_domain={},
            meaning_events_28d=1,
        )
    )
    db_session.commit()

    baseline = find_baseline_snapshot_for_delta_30d(
        db_session, user_id=history_user.id, reference_date=ref
    )
    assert baseline is None


def test_build_cum_persists_snapshot_and_delta(db_session: Session, history_user: User):
    ref = date(2026, 7, 2)
    db_session.add(
        CumConfidenceSnapshot(
            user_id=history_user.id,
            snapshot_date=ref - timedelta(days=30),
            overall=0.35,
            by_domain={},
            meaning_events_28d=2,
        )
    )
    db_session.commit()

    payload = build_compact_user_model_v0(
        db_session,
        user_id=history_user.id,
        reference_date=ref,
    )
    assert payload["confidence"]["delta_30d"] is not None
    assert payload["confidence"]["delta_30d"] == round(
        payload["confidence"]["overall"] - 0.35, 3
    )

    today_row = (
        db_session.query(CumConfidenceSnapshot)
        .filter(
            CumConfidenceSnapshot.user_id == history_user.id,
            CumConfidenceSnapshot.snapshot_date == ref,
        )
        .one()
    )
    assert today_row.overall == payload["confidence"]["overall"]


def test_load_confidence_history_window_and_summary(db_session: Session, history_user: User):
    ref = date(2026, 7, 2)
    for offset, overall in ((0, 0.4), (15, 0.5), (30, 0.55), (60, 0.62)):
        db_session.add(
            CumConfidenceSnapshot(
                user_id=history_user.id,
                snapshot_date=ref - timedelta(days=offset),
                overall=overall,
                by_domain={"identity": overall - 0.05},
                meaning_events_28d=offset,
            )
        )
    db_session.commit()

    payload = load_cum_confidence_history_v0(
        db_session,
        user_id=history_user.id,
        reference_date=ref,
        window_days=90,
    )
    assert payload["contract_version"] == "cum_confidence_history_v0"
    assert payload["window_days"] == 90
    assert payload["start_date"] == (ref - timedelta(days=89)).isoformat()
    assert len(payload["points"]) == 4
    assert payload["summary"]["point_count"] == 4
    assert payload["summary"]["overall_min"] == 0.4
    assert payload["summary"]["overall_max"] == 0.62
    assert payload["summary"]["delta_window"] == round(0.4 - 0.62, 3)


def test_load_confidence_history_respects_smaller_window(db_session: Session, history_user: User):
    ref = date(2026, 7, 2)
    db_session.add(
        CumConfidenceSnapshot(
            user_id=history_user.id,
            snapshot_date=ref - timedelta(days=40),
            overall=0.3,
            by_domain={},
            meaning_events_28d=1,
        )
    )
    db_session.add(
        CumConfidenceSnapshot(
            user_id=history_user.id,
            snapshot_date=ref - timedelta(days=5),
            overall=0.45,
            by_domain={},
            meaning_events_28d=2,
        )
    )
    db_session.commit()

    payload = load_cum_confidence_history_v0(
        db_session,
        user_id=history_user.id,
        reference_date=ref,
        window_days=30,
    )
    assert len(payload["points"]) == 1
    assert payload["points"][0]["snapshot_date"] == (ref - timedelta(days=5)).isoformat()
