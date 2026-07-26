"""Day Lifecycle C5.1–C5.3 jobs — pre-warm assemble, ready gate helpers, system close.

Canon: docs/audits/DAY_LIFECYCLE_V1.md
Hooked from POST /internal/push/run-due (same cron secret).
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.db import models as db_models
from todayflow_backend.db.models import User
from todayflow_backend.services.day_lifecycle_clock_c5 import (
    DEFAULT_ASSEMBLE_START,
    DEFAULT_CLOSE_TIME,
    DEFAULT_TIMEZONE,
    in_assemble_window,
    local_now,
    should_system_close_date,
)
from todayflow_backend.services.push_delivery import _schedule_row

logger = logging.getLogger(__name__)

READY_SOURCES = frozenset({"native_llm_c1", "deterministic_engine_b5"})
SYSTEM_CLOSE_MARKER = "system_close_c5"


def day_story_is_product_ready(db: Session, *, user_id: int, local_date: date) -> bool:
    """True when a ready native/deterministic scenario exists for the date."""
    from todayflow_backend.services.day_story_wire_v1 import _load_cached_day_story

    hit = _load_cached_day_story(
        db,
        user_id=int(user_id),
        target_date=local_date,
        any_for_date=True,
    )
    if hit is None:
        return False
    story, _, _ = hit
    sc = story.get("day_scenario") if isinstance(story.get("day_scenario"), dict) else {}
    return bool(sc.get("ready") and sc.get("scenes") and str(sc.get("generation_source") or "") in READY_SOURCES)


def _minimal_morning(target_date: date):
    from todayflow_backend.api.morning_ritual import MorningRitualResponse

    return MorningRitualResponse.model_construct(
        date=target_date.isoformat(),
        energy_level=5,
        focus_areas=[],
        daily_recommendations={},
        ritual_completed=False,
        tarot_card={},
        tarot_explanation={},
        numerology_number={},
        numerology_explanation={},
        celestial_events={},
    )


def prewarm_assemble_user_day(
    db: Session,
    *,
    user: User,
    local_date: date,
    timezone_name: str,
    locale: str = "ru",
) -> str:
    """
    Assemble once for (user, local_date) if missing.
    Returns: skipped_ready | rebuilt | unchanged | error
    """
    if day_story_is_product_ready(db, user_id=int(user.id), local_date=local_date):
        return "skipped_ready"

    from todayflow_backend.services.core_profile import get_core_profile_service
    from todayflow_backend.services.day_story_refresh_v1 import refresh_day_story_for_user
    from todayflow_backend.services.day_story_wire_v1 import build_day_story_record_for_refresh

    morning = _minimal_morning(local_date)
    core_profile = get_core_profile_service().build_cached_or_baseline(db, user)
    fusion_dump: dict[str, Any] = {}

    def _build(db_sess, **kwargs):
        return build_day_story_record_for_refresh(
            db_sess,
            user=kwargs["user"],
            target_date=kwargs["target_date"],
            locale=kwargs["locale"],
            morning=morning,
            fusion_dump=fusion_dump,
            core_profile=core_profile if isinstance(core_profile, dict) else {},
            force_rebuild=kwargs.get("force_rebuild", True),
            expected_fingerprint=kwargs.get("expected_fingerprint"),
            fingerprint_payload=kwargs.get("fingerprint_payload"),
            timezone_name=timezone_name,
        )

    try:
        result = refresh_day_story_for_user(
            db,
            user=user,
            local_date=local_date,
            timezone_name=timezone_name,
            locale=locale,
            build_fn=_build,
            force=True,
        )
        if result.get("rebuilt"):
            return "rebuilt"
        if day_story_is_product_ready(db, user_id=int(user.id), local_date=local_date):
            return "skipped_ready"
        return "unchanged"
    except Exception as exc:
        logger.warning("prewarm_assemble failed user=%s date=%s: %s", user.id, local_date, exc)
        return "error"


def system_close_user_day(db: Session, *, user_id: int, local_date: date) -> str:
    """
    Mark evening completed when user did not close.
    Returns: closed | already_closed | skipped
    """
    row = (
        db.query(db_models.DayConnection)
        .filter(
            db_models.DayConnection.user_id == int(user_id),
            db_models.DayConnection.date == local_date,
        )
        .first()
    )
    if row is None:
        row = db_models.DayConnection(user_id=int(user_id), date=local_date)
        db.add(row)

    if bool(row.evening_completed):
        return "already_closed"

    obs = row.evening_observations if isinstance(row.evening_observations, dict) else {}
    obs = {
        **obs,
        SYSTEM_CLOSE_MARKER: True,
        "closed_at": datetime.now(timezone.utc).replace(tzinfo=None).isoformat() + "Z",
        "closed_by": "system",
    }
    row.evening_completed = True
    row.evening_observations = obs
    if not (row.evening_reflection or "").strip():
        row.evening_reflection = "День закрыт системой — вечером не было ручного закрытия."
    db.add(row)

    ritual = (
        db.query(db_models.DayRitual)
        .filter(
            db_models.DayRitual.user_id == int(user_id),
            db_models.DayRitual.date == local_date,
        )
        .first()
    )
    if ritual is None:
        ritual = db_models.DayRitual(user_id=int(user_id), date=local_date)
        db.add(ritual)
    if not bool(ritual.completed):
        ritual.completed = True
        ritual.sufficiency_confirmed = True
        ritual.ritual_type = ritual.ritual_type or "system_close"
        db.add(ritual)

    db.commit()
    return "closed"


def _candidate_user_ids(db: Session) -> list[int]:
    """Users with push devices (active delivery surface) — same set as push cron."""
    return [int(r[0]) for r in db.query(db_models.PushDevice.user_id).distinct().all()]


def run_day_lifecycle_due(
    db: Session,
    *,
    now_utc: datetime | None = None,
    max_prewarm: int = 8,
) -> dict[str, int]:
    """C5.1 pre-warm + C5.3 system close for users in local windows."""
    now_utc = now_utc or datetime.now(timezone.utc)
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=timezone.utc)

    counts = {
        "prewarm_rebuilt": 0,
        "prewarm_skipped_ready": 0,
        "prewarm_unchanged": 0,
        "prewarm_error": 0,
        "prewarm_candidates": 0,
        "system_closed": 0,
        "system_already_closed": 0,
        "system_close_candidates": 0,
    }

    prewarm_budget = max(0, int(max_prewarm))
    for uid in _candidate_user_ids(db):
        user = db.query(User).filter(User.id == uid).first()
        if user is None:
            continue
        sched_row = (
            db.query(db_models.UserPushSchedule)
            .filter(db_models.UserPushSchedule.user_id == uid)
            .first()
        )
        sch = _schedule_row(sched_row)
        tz_name = sch.get("timezone") or DEFAULT_TIMEZONE
        now_local = local_now(now=now_utc, timezone_name=tz_name)
        local_date = now_local.date()
        locale = "en" if (user.settings and (user.settings.locale or "").lower().startswith("en")) else "ru"

        # C5.3 system close — today after 23:00 and yesterday after assemble opens
        for candidate in (local_date, local_date - timedelta(days=1)):
            if not should_system_close_date(
                now_local=now_local,
                candidate=candidate,
                close_time=DEFAULT_CLOSE_TIME,
                assemble_start=DEFAULT_ASSEMBLE_START,
            ):
                continue
            counts["system_close_candidates"] += 1
            outcome = system_close_user_day(db, user_id=uid, local_date=candidate)
            if outcome == "closed":
                counts["system_closed"] += 1
            elif outcome == "already_closed":
                counts["system_already_closed"] += 1

        # C5.1 pre-warm — only in assemble window, budgeted
        if prewarm_budget <= 0:
            continue
        if not in_assemble_window(
            now_local,
            assemble_start=DEFAULT_ASSEMBLE_START,
            assemble_end=DEFAULT_ASSEMBLE_END,
        ):
            continue
        counts["prewarm_candidates"] += 1
        outcome = prewarm_assemble_user_day(
            db,
            user=user,
            local_date=local_date,
            timezone_name=tz_name,
            locale=locale,
        )
        key = {
            "rebuilt": "prewarm_rebuilt",
            "skipped_ready": "prewarm_skipped_ready",
            "unchanged": "prewarm_unchanged",
            "error": "prewarm_error",
        }.get(outcome, "prewarm_error")
        counts[key] += 1
        if outcome == "rebuilt":
            prewarm_budget -= 1

    return counts
