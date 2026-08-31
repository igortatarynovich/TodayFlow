"""Wave 2 Phase A — tap_event_v1 + accuracy-summary."""

from datetime import date, timedelta

from todayflow_backend.db.models import User
from todayflow_backend.db import models as db_models
from todayflow_backend.services import today_tap_widget_v1 as tap_svc


def _user(db_session) -> User:
    user = User(email="tap-widget@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_upsert_tap_and_accuracy_denominator(db_session):
    user = _user(db_session)
    day = date.today()
    a = tap_svc.upsert_tap_event(
        db_session,
        user_id=user.id,
        local_date=day,
        scene_id="scene.work_decisions",
        prompted_text="Отложить и сделать вид, что выбора нет.",
        response="avoided_trap",
        domain="work",
    )
    assert a["schema_version"] == "tap_event_v1"
    assert a["day_facts_id"] == f"{user.id}:{day.isoformat()}"
    assert a["response"] == "avoided_trap"

    tap_svc.upsert_tap_event(
        db_session,
        user_id=user.id,
        local_date=day - timedelta(days=1),
        scene_id="scene.money",
        prompted_text="Купить от скуки.",
        response="fell_into_trap",
        domain="money",
    )
    tap_svc.upsert_tap_event(
        db_session,
        user_id=user.id,
        local_date=day - timedelta(days=2),
        scene_id="scene.rel",
        prompted_text="Молчать.",
        response="not_applicable",
        domain="relationships",
    )
    tap_svc.upsert_tap_event(
        db_session,
        user_id=user.id,
        local_date=day - timedelta(days=3),
        scene_id="scene.skip",
        prompted_text="Пропуск.",
        response="skipped",
        domain="energy",
    )

    summary = tap_svc.build_accuracy_summary(db_session, user_id=user.id, window_days=14)
    assert summary["overall"] == {"correct": 1, "total": 2}
    assert summary["by_domain"]["work"] == {"correct": 1, "total": 1}
    assert summary["by_domain"]["money"] == {"correct": 0, "total": 1}
    assert summary["by_domain"]["relationships"] == {"correct": 0, "total": 0}
    assert summary["by_domain"]["energy"] == {"correct": 0, "total": 0}


def test_tap_idempotent_per_day_scene(db_session):
    user = _user(db_session)
    day = date(2026, 7, 29)
    first = tap_svc.upsert_tap_event(
        db_session,
        user_id=user.id,
        local_date=day,
        scene_id="scene.work_decisions",
        prompted_text="Trap A",
        response="fell_into_trap",
        domain="work",
    )
    second = tap_svc.upsert_tap_event(
        db_session,
        user_id=user.id,
        local_date=day,
        scene_id="scene.work_decisions",
        prompted_text="Trap A updated",
        response="avoided_trap",
        domain="work",
    )
    assert first["event_id"] == second["event_id"]
    assert second["response"] == "avoided_trap"
    assert second["prompted_text"] == "Trap A updated"
    count = (
        db_session.query(db_models.TodayTapEvent)
        .filter(db_models.TodayTapEvent.user_id == user.id)
        .count()
    )
    assert count == 1


def test_map_sphere_to_domain():
    assert tap_svc.map_sphere_to_domain("work_decisions") == "work"
    assert tap_svc.map_sphere_to_domain("money") == "money"
    assert tap_svc.map_sphere_to_domain("relationships") == "relationships"
