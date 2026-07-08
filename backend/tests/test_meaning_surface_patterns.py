"""DE-5: агрегаты `meaning_events` для DayContext / learning."""

from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from todayflow_backend.db.models import MeaningEvent, User
from todayflow_backend.services.auth import hash_password
from todayflow_backend.services.learning import LearningService
from todayflow_backend.services.meaning_surface_patterns import build_meaning_surface_patterns_v0


@pytest.fixture
def pattern_user(db_session: Session) -> User:
    u = User(
        email="pattern_agg@example.com",
        password_hash=hash_password("secret12345"),
        is_paid=False,
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


def _evt(
    user_id: int,
    *,
    local_date: date,
    event_type: str,
    idem: str,
    payload: dict | None = None,
) -> MeaningEvent:
    return MeaningEvent(
        event_id=str(uuid4())[:32],
        user_id=user_id,
        event_type=event_type,
        event_source="today",
        local_date=local_date,
        quality_score=0.9,
        payload=payload,
        idempotency_key=idem,
    )


def test_build_meaning_surface_patterns_v0_none_when_empty(db_session: Session, pattern_user: User) -> None:
    ref = date(2026, 5, 10)
    assert build_meaning_surface_patterns_v0(db_session, user_id=pattern_user.id, reference_date=ref) is None


def test_build_meaning_surface_patterns_v0_mood_and_hints(db_session: Session, pattern_user: User) -> None:
    ref = date(2026, 5, 10)
    uid = pattern_user.id
    for i in range(4):
        db_session.add(
            _evt(
                uid,
                local_date=ref,
                event_type="focus_started",
                idem=f"fs-{i}",
                payload={"duration_minutes": 20},
            )
        )
    for i in range(3):
        db_session.add(
            _evt(
                uid,
                local_date=ref,
                event_type="mood_selected",
                idem=f"m-{i}",
                payload={"mood_id": "calm"},
            )
        )
    db_session.commit()

    out = build_meaning_surface_patterns_v0(db_session, user_id=uid, reference_date=ref, window_days=14)
    assert out is not None
    assert out["contract_version"] == "meaning_surface_patterns_v0"
    assert out["total_events"] == 7
    assert out["tags"]["focus_sessions_started"] == 4
    mood_top = out["tags"]["top_mood_ids"]
    assert mood_top and mood_top[0]["id"] == "calm" and mood_top[0]["count"] == 3
    assert any("фокус" in h.lower() for h in out["pattern_hints"])


def test_build_meaning_surface_patterns_v0_proximity_and_guidance(
    db_session: Session, pattern_user: User
) -> None:
    ref = date(2026, 7, 5)
    uid = pattern_user.id
    for i in range(3):
        db_session.add(
            _evt(
                uid,
                local_date=ref,
                event_type="sphere_feedback",
                idem=f"sf-{i}",
                payload={
                    "target": "tarot_impact",
                    "proximity_choice": "first_step",
                    "echo": "yes",
                    "interpretation_confirm": True,
                },
            )
        )
    for i in range(2):
        db_session.add(
            _evt(
                uid,
                local_date=ref,
                event_type="guidance_ask",
                idem=f"g-{i}",
                payload={"surface": "questions"},
            )
        )
    db_session.commit()

    out = build_meaning_surface_patterns_v0(db_session, user_id=uid, reference_date=ref, window_days=14)
    assert out is not None
    prox = out["tags"]["ritual_proximity"]["top_choices"]
    assert prox and prox[0]["id"] == "first_step" and prox[0]["count"] == 3
    assert out["tags"]["guidance_questions_asked"] == 2
    assert any("первый шаг" in h.lower() or "first_step" in h for h in out["pattern_hints"])
    assert any("вопрос" in h.lower() for h in out["pattern_hints"])


def test_compact_user_model_behavioral_from_proximity(db_session: Session, pattern_user: User) -> None:
    from todayflow_backend.services.compact_user_model_v0 import build_compact_user_model_v0

    ref = date(2026, 7, 5)
    uid = pattern_user.id
    for i in range(4):
        db_session.add(
            _evt(
                uid,
                local_date=ref,
                event_type="sphere_feedback",
                idem=f"sf-cum-{i}",
                payload={"target": "number_impact", "proximity_choice": "wait", "echo": "partial"},
            )
        )
    db_session.commit()

    cum = build_compact_user_model_v0(db_session, user_id=uid, reference_date=ref, window_days=14)
    behavioral = cum["behavioral_patterns"]
    assert "ritual_proximity:wait" in behavioral["works"]
    assert cum["current_state"]["ritual_proximity_choice"] == "wait"
    assert cum["current_state"]["ritual_proximity_target"] == "number_impact"


def test_build_meaning_surface_patterns_v0_honest_step_day_promise_guidance_themes(
    db_session: Session, pattern_user: User
) -> None:
    ref = date(2026, 7, 5)
    uid = pattern_user.id
    for i in range(3):
        db_session.add(
            _evt(
                uid,
                local_date=ref,
                event_type="sphere_feedback",
                idem=f"hs-{i}",
                payload={"target": "tarot_impact", "tarot_honest_step": "work"},
            )
        )
    for i in range(2):
        db_session.add(
            _evt(
                uid,
                local_date=ref,
                event_type="action_option_selected",
                idem=f"dp-{i}",
                payload={"action": "day_promise_set", "promise_text": f"Сделать задачу {i}"},
            )
        )
    db_session.add(
        _evt(
            uid,
            local_date=ref,
            event_type="guidance_ask",
            idem="g-work",
            payload={"lane": "career", "question": "Как не выгореть на работе?"},
        )
    )
    db_session.add(
        _evt(
            uid,
            local_date=ref,
            event_type="guidance_ask",
            idem="g-work-2",
            payload={"lane": "career", "question": "Стоит ли менять проект на работе?"},
        )
    )
    db_session.commit()

    out = build_meaning_surface_patterns_v0(db_session, user_id=uid, reference_date=ref, window_days=14)
    assert out is not None
    tags = out["tags"]
    assert tags["top_honest_step_ids"][0]["id"] == "work" and tags["top_honest_step_ids"][0]["count"] == 3
    assert tags["day_promise_sets"] == 2
    assert tags["top_guidance_lanes"][0]["id"] == "career"
    theme_ids = {item["id"] for item in tags["top_guidance_themes"]}
    assert "lane:career" in theme_ids
    assert "topic:работа" in theme_ids
    assert any("честный шаг" in h.lower() for h in out["pattern_hints"])
    assert any("обещание дня" in h.lower() for h in out["pattern_hints"])


def test_compact_user_model_active_themes_from_guidance(db_session: Session, pattern_user: User) -> None:
    from todayflow_backend.services.compact_user_model_v0 import build_compact_user_model_v0

    ref = date(2026, 7, 5)
    uid = pattern_user.id
    for i in range(3):
        db_session.add(
            _evt(
                uid,
                local_date=ref,
                event_type="guidance_ask",
                idem=f"g-{i}",
                payload={"lane": "relations", "question": "Как поговорить с партнёром?"},
            )
        )
    db_session.add(
        _evt(
            uid,
            local_date=ref,
            event_type="sphere_feedback",
            idem="hs-latest",
            payload={"tarot_honest_step": "relations"},
        )
    )
    db_session.commit()

    cum = build_compact_user_model_v0(db_session, user_id=uid, reference_date=ref, window_days=14)
    theme_ids = {t["id"] for t in cum["active_themes"]}
    assert "lane:relations" in theme_ids or "topic:отношения" in theme_ids
    assert cum["current_state"]["honest_step_id"] == "relations"
    assert "day_promise_habit" not in cum["behavioral_patterns"]["works"]


def test_learning_context_includes_meaning_patterns(db_session: Session, pattern_user: User) -> None:
    ref = date(2026, 5, 11)
    db_session.add(
        _evt(
            pattern_user.id,
            local_date=ref,
            event_type="evening_reflection_submitted",
            idem="ev-1",
            payload={"evening_completed": True},
        )
    )
    db_session.commit()
    svc = LearningService()
    ctx = svc.build_user_learning_context(db_session, user_id=pattern_user.id, target_date=ref)
    assert ctx["stats"]["meaning_events_28d"] >= 1
    assert "meaning_surface_patterns" in ctx
    assert ctx["meaning_surface_patterns"]["total_events"] >= 1
