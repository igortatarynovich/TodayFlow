"""DE-9: history_layer_v0 — вчера, 7 дней, дельта к вчера."""

from __future__ import annotations

from datetime import date

from todayflow_backend.db import models as db_models
from todayflow_backend.services.auth import hash_password
from todayflow_backend.services.history_layer_v0 import build_history_layer_v0


def test_build_history_layer_v0_contract_and_yesterday_date(db_session):
    u = db_models.User(email="de9-history@example.com", password_hash=hash_password("pw"))
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    h = build_history_layer_v0(
        db_session,
        user_id=u.id,
        target_date=date(2026, 5, 10),
        today_fusion_scores={"energy": 55, "emotional_balance": 60, "focus": 52},
    )
    assert h["contract_version"] == "day_history_v0"
    assert h["yesterday"]["date"] == "2026-05-09"
    assert set(h["yesterday"]["fusion_scores"].keys()) == {"energy", "emotional_balance", "focus"}
    assert len(h["fusion_scores_trailing_7d"]) == 7
    assert h["fusion_scores_trailing_7d"][0]["date"] == "2026-05-09"
    summ = h["trailing_7d_summary"]
    assert set(summ.keys()) == {"energy", "emotional_balance", "focus"}
    for axis in ("energy", "emotional_balance", "focus"):
        assert set(summ[axis].keys()) == {"avg", "min", "max", "days"}
        assert summ[axis]["days"] == 7
    dlt = h["fusion_score_delta_vs_yesterday"]
    ye = int(h["yesterday"]["fusion_scores"]["energy"])
    assert dlt["energy"] == 55 - ye
    assert h.get("fusion_score_delta_trustworthy") is False
    assert h.get("yesterday_fusion_has_flow_markers") is False
    assert h.get("trailing_7d_flow_days") == 0
    assert h.get("trailing_7d_summary_trustworthy") is False


def test_build_history_layer_v0_delta_trustworthy_true_when_yesterday_has_mood(db_session):
    u = db_models.User(email="de9-history-mood@example.com", password_hash=hash_password("pw"))
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    yday = date(2026, 5, 9)
    db_session.add(
        db_models.ProgressTrackerEntry(
            user_id=u.id,
            date=yday,
            completed=False,
            state_scale=4,
        )
    )
    db_session.commit()

    h = build_history_layer_v0(
        db_session,
        user_id=u.id,
        target_date=date(2026, 5, 10),
        today_fusion_scores={"energy": 55, "emotional_balance": 60, "focus": 52},
    )
    assert h.get("fusion_score_delta_trustworthy") is True
    assert h.get("yesterday_fusion_has_flow_markers") is True
    assert h.get("trailing_7d_flow_days") == 1
    assert h.get("trailing_7d_summary_trustworthy") is True


def test_build_history_layer_v0_week_trustworthy_without_yesterday_flow(db_session):
    """O7: вчера без отметок — дельта нечестна, но в окне 7 дней есть другой день с Flow — сводка недели ок."""
    u = db_models.User(email="de9-history-split@example.com", password_hash=hash_password("pw"))
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    day_with_mood = date(2026, 5, 8)
    db_session.add(
        db_models.ProgressTrackerEntry(
            user_id=u.id,
            date=day_with_mood,
            completed=False,
            state_scale=3,
        )
    )
    db_session.commit()

    h = build_history_layer_v0(
        db_session,
        user_id=u.id,
        target_date=date(2026, 5, 10),
        today_fusion_scores={"energy": 60, "emotional_balance": 55, "focus": 58},
    )
    assert h.get("fusion_score_delta_trustworthy") is False
    assert h.get("trailing_7d_summary_trustworthy") is True
    assert int(h.get("trailing_7d_flow_days") or 0) >= 1


def test_build_history_layer_v0_yesterday_meaning_signals(db_session):
    u = db_models.User(email="de9-history-meaning@example.com", password_hash=hash_password("pw"))
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    yday = date(2026, 5, 9)
    db_session.add(
        db_models.MeaningEvent(
            event_id="de9-habit-1",
            user_id=u.id,
            event_type="habit_completed",
            event_source="today",
            local_date=yday,
            quality_score=1.0,
            idempotency_key="de9-habit-1",
        )
    )
    db_session.add(
        db_models.MeaningEvent(
            event_id="de9-sphere-1",
            user_id=u.id,
            event_type="sphere_opened",
            event_source="today",
            local_date=yday,
            quality_score=1.0,
            idempotency_key="de9-sphere-1",
        )
    )
    db_session.commit()

    h = build_history_layer_v0(
        db_session,
        user_id=u.id,
        target_date=date(2026, 5, 10),
        today_fusion_scores={"energy": 55, "emotional_balance": 60, "focus": 52},
    )
    y = h["yesterday"]
    assert y.get("meaning_active") is True
    assert y.get("meaning_completions_total") == 1
    signals = y.get("meaning_day_signals")
    assert isinstance(signals, dict)
    assert signals.get("habit_completed") == 1
    assert signals.get("sphere_opened") == 1
    assert int(h.get("trailing_7d_meaning_active_days") or 0) >= 1
    series0 = h["fusion_scores_trailing_7d"][0]
    assert series0.get("meaning_active") is True
    assert series0.get("meaning_completions_total") == 1


def test_build_history_layer_v0_reflection_excerpt(db_session):
    u = db_models.User(email="de9-history-reflect@example.com", password_hash=hash_password("pw"))
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    yday = date(2026, 5, 9)
    db_session.add(
        db_models.DayConnection(
            user_id=u.id,
            date=yday,
            evening_reflection="Получилось закрыть одну задачу и не разгонять чаты.",
            morning_intention="Спокойный фокус на работе",
            evening_completed=True,
        )
    )
    db_session.commit()

    h = build_history_layer_v0(
        db_session,
        user_id=u.id,
        target_date=date(2026, 5, 10),
        today_fusion_scores={"energy": 55, "emotional_balance": 60, "focus": 52},
    )
    ex = h["yesterday"].get("reflection_excerpt")
    assert isinstance(ex, dict)
    assert ex.get("contract_version") == "day_connection_excerpt_v0"
    assert ex.get("has_reflection") is True
    assert "задачу" in str(ex.get("evening_reflection") or "")
