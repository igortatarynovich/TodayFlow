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
    DEFAULT_ASSEMBLE_END,
    DEFAULT_ASSEMBLE_START,
    DEFAULT_CLOSE_TIME,
    DEFAULT_READY_TIME,
    DEFAULT_TIMEZONE,
    in_assemble_window,
    in_d_minus_1_window,
    local_now,
    parse_hhmm,
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
    source = str(sc.get("generation_source") or "")
    if source not in READY_SOURCES:
        return False
    if sc.get("narrative_omitted"):
        return True
    return bool(sc.get("ready") and sc.get("scenes"))


def _minimal_morning(target_date: date, *, celestial_events: dict[str, Any] | None = None):
    from todayflow_backend.api.morning_ritual import MorningRitualResponse

    return MorningRitualResponse.model_construct(
        date=target_date.isoformat(),
        energy_level=5,
        focus_areas=[],
        daily_recommendations={
            "what_to_do": "",
            "what_to_avoid": "",
            "key_focus": "general",
        },
        ritual_completed=False,
        tarot_card={},
        tarot_explanation={},
        numerology_number={},
        numerology_explanation={},
        celestial_events=celestial_events if isinstance(celestial_events, dict) else {},
    )


def _build_prewarm_celestial(local_date: date, locale: str) -> dict[str, Any]:
    """Sky pack for assemble-once — best-effort, never blocks pre-warm."""
    try:
        import asyncio

        from todayflow_backend.services import astro
        from todayflow_backend.services.celestial_events_builder import build_celestial_events

        coro = build_celestial_events(
            local_date,
            locale,
            personal_day=None,
            personal_transits=[],
            astro_service=astro.AstroService(),
        )
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            # Cron path is sync; nested loop is unexpected — skip sky rather than deadlock.
            return {}
        return asyncio.run(coro) or {}
    except Exception as exc:
        logger.warning("prewarm celestial_events failed date=%s: %s", local_date, exc)
        return {}


def _fusion_dump_for_user(db: Session, *, user: User, local_date: date) -> dict[str, Any]:
    try:
        from todayflow_backend.api.tracking import get_daily_fusion_index

        fusion = get_daily_fusion_index(
            target_date=local_date.isoformat(),
            current_user=user,
            db=db,
        )
        return fusion.model_dump() if hasattr(fusion, "model_dump") else dict(fusion or {})
    except Exception as exc:
        logger.warning("prewarm fusion failed user=%s date=%s: %s", user.id, local_date, exc)
        return {}


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
    Lays out story/scenario + prebaked card/number. Returns: skipped_ready | rebuilt | unchanged | error
    """
    from todayflow_backend.services.day_symbol_state_v1 import (
        ensure_symbols_prebaked,
        owner_key_for_user,
    )

    owner_key = owner_key_for_user(int(user.id))
    # Symbols are part of the day package even when story is already ready.
    try:
        ensure_symbols_prebaked(
            db,
            owner_key=owner_key,
            local_date=local_date,
            timezone_name=timezone_name,
            user_id=int(user.id),
            locale=locale,
        )
    except Exception as sym_exc:
        logger.warning(
            "prewarm symbol prebake failed user=%s date=%s: %s",
            user.id,
            local_date,
            sym_exc,
        )

    story_status = "pending"
    if day_story_is_product_ready(db, user_id=int(user.id), local_date=local_date):
        story_status = "skipped_ready"
    else:
        from todayflow_backend.services.core_profile import get_core_profile_service
        from todayflow_backend.services.day_story_refresh_v1 import refresh_day_story_for_user
        from todayflow_backend.services.day_story_wire_v1 import build_day_story_record_for_refresh

        celestial = _build_prewarm_celestial(local_date, locale)
        morning = _minimal_morning(local_date, celestial_events=celestial)
        core_profile = get_core_profile_service().build_cached_or_baseline(db, user)
        fusion_dump = _fusion_dump_for_user(db, user=user, local_date=local_date)

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
                story_status = "rebuilt"
            elif day_story_is_product_ready(db, user_id=int(user.id), local_date=local_date):
                story_status = "skipped_ready"
            else:
                story_status = "unchanged"
        except Exception as exc:
            logger.warning("prewarm_assemble failed user=%s date=%s: %s", user.id, local_date, exc)
            story_status = "error"

    # Activity-window copy for Поток дня (Kimi) — own short-lived session so the
    # job transaction is not held across Nebius (~15s) and GET /day-facts stays fast.
    try:
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass

    try:
        from todayflow_backend.db.session import SessionLocal
        from todayflow_backend.services.day_flow_windows_kimi_v1 import (
            ensure_day_flow_windows_for_user,
        )

        flow_db = SessionLocal()
        try:
            flow_user = flow_db.query(User).filter(User.id == int(user.id)).one()
            flow_status = ensure_day_flow_windows_for_user(
                flow_db,
                user=flow_user,
                local_date=local_date,
                timezone_name=timezone_name,
                locale=locale,
            )
            logger.info(
                "prewarm day_flow_windows user=%s date=%s status=%s",
                user.id,
                local_date,
                flow_status,
            )
        finally:
            flow_db.close()
    except Exception as flow_exc:
        logger.warning(
            "prewarm day_flow_windows failed user=%s date=%s: %s",
            user.id,
            local_date,
            flow_exc,
        )

    return story_status


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
    """Users who should receive assemble-once: profile-ready + push + recent activity."""
    ids: set[int] = set()
    for (uid,) in db.query(db_models.PushDevice.user_id).distinct().all():
        if uid is not None:
            ids.add(int(uid))
    for (uid,) in db.query(db_models.UserPushSchedule.user_id).distinct().all():
        if uid is not None:
            ids.add(int(uid))
    # Profile-capable accounts (birth facts) — morning package even without recent open.
    for (uid,) in (
        db.query(db_models.AstroProfile.user_id)
        .filter(
            (db_models.AstroProfile.is_primary.is_(True))
            | (db_models.AstroProfile.relation.is_(None))
            | (db_models.AstroProfile.relation == "self")
        )
        .distinct()
        .all()
    ):
        if uid is not None:
            ids.add(int(uid))
    # Recent day engagement — don't leave active users without a morning package.
    recent_cut = date.today() - timedelta(days=3)
    for (uid,) in (
        db.query(db_models.DayConnection.user_id)
        .filter(db_models.DayConnection.date >= recent_cut)
        .distinct()
        .all()
    ):
        if uid is not None:
            ids.add(int(uid))
    # Broader activity signals (14d) — MeaningEvent / day_story pipeline.
    activity_cut = date.today() - timedelta(days=14)
    for (uid,) in (
        db.query(db_models.MeaningEvent.user_id)
        .filter(db_models.MeaningEvent.local_date >= activity_cut)
        .distinct()
        .all()
    ):
        if uid is not None:
            ids.add(int(uid))
    for (uid,) in (
        db.query(db_models.DayStoryState.user_id)
        .filter(
            db_models.DayStoryState.user_id.isnot(None),
            db_models.DayStoryState.local_date >= activity_cut,
        )
        .distinct()
        .all()
    ):
        if uid is not None:
            ids.add(int(uid))
    return _exclude_synthetic_prewarm_ids(db, ids)


def _exclude_synthetic_prewarm_ids(db: Session, ids: set[int]) -> list[int]:
    """Production prewarm must not spend on RFC 2606 example.com fixtures."""
    if not ids:
        return []
    from todayflow_backend.core.llm_cost_guard_v1 import is_synthetic_production_email

    rows = db.query(User.id, User.email).filter(User.id.in_(list(ids))).all()
    keep: list[int] = []
    for uid, email in rows:
        if is_synthetic_production_email(str(email or "")):
            logger.info("day_prewarm skip synthetic email user_id=%s", uid)
            continue
        keep.append(int(uid))
    return sorted(keep)


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
        "prewarm_enqueued": 0,
        "prewarm_candidates": 0,
        "prewarm_d_minus_1": 0,
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

        # C5.1 pre-warm — today assemble/catch-up, plus D−1 evening for tomorrow.
        if prewarm_budget <= 0:
            continue
        ready_t = parse_hhmm(sch.get("morning_time"), fallback=DEFAULT_READY_TIME)
        past_ready = (now_local.hour * 60 + now_local.minute) >= (ready_t.hour * 60 + ready_t.minute)
        needs_catchup = past_ready and not day_story_is_product_ready(
            db, user_id=uid, local_date=local_date
        )
        in_today_assemble = in_assemble_window(
            now_local,
            assemble_start=DEFAULT_ASSEMBLE_START,
            assemble_end=DEFAULT_ASSEMBLE_END,
        ) or needs_catchup
        d_minus_1 = in_d_minus_1_window(now_local)
        if not in_today_assemble and not d_minus_1:
            continue
        from todayflow_backend.services.day_prewarm_job_c5 import enqueue_day_prewarm

        if in_today_assemble:
            counts["prewarm_candidates"] += 1
            if day_story_is_product_ready(db, user_id=uid, local_date=local_date):
                counts["prewarm_skipped_ready"] += 1
            elif prewarm_budget > 0:
                enqueue_day_prewarm(
                    db,
                    user_id=uid,
                    local_date=local_date,
                    locale=locale,
                    timezone_name=tz_name,
                )
                counts["prewarm_enqueued"] += 1
                prewarm_budget -= 1

        if d_minus_1 and prewarm_budget > 0:
            tomorrow = local_date + timedelta(days=1)
            counts["prewarm_candidates"] += 1
            if day_story_is_product_ready(db, user_id=uid, local_date=tomorrow):
                counts["prewarm_skipped_ready"] += 1
            else:
                enqueue_day_prewarm(
                    db,
                    user_id=uid,
                    local_date=tomorrow,
                    locale=locale,
                    timezone_name=tz_name,
                )
                counts["prewarm_enqueued"] += 1
                counts["prewarm_d_minus_1"] += 1
                prewarm_budget -= 1

    return counts
