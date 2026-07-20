"""Full guest → user claim: session, progress SoT, protected token, atomic transfer."""

from __future__ import annotations

import hashlib
import logging
import secrets
from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from todayflow_backend.db import models as db_models
from todayflow_backend.db.models import utc_naive_now
from todayflow_backend.services.day_story_v1 import DAY_STORY_V1_CONTRACT
from todayflow_backend.services.day_symbol_state_v1 import (
    claim_guest_symbols_to_user,
    owner_key_for_guest,
    owner_key_for_user,
)

logger = logging.getLogger(__name__)

GUEST_CLAIM_V1 = "guest_claim_v1"
CLAIM_TOKEN_TTL = timedelta(minutes=30)
DEFAULT_REDIRECT = "/today?first=1"


def _hash_secret(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _new_token() -> str:
    return secrets.token_urlsafe(32)


def ensure_guest_session(
    db: Session,
    *,
    guest_session_id: str | None = None,
    locale: str | None = None,
    timezone_name: str | None = None,
) -> dict[str, Any]:
    """Create or return guest session. Returns plaintext session_secret only on create."""
    gid = (guest_session_id or "").strip() or secrets.token_urlsafe(18)
    if len(gid) > 64:
        raise ValueError("invalid_guest_session_id")
    existing = (
        db.query(db_models.GuestSession)
        .filter(db_models.GuestSession.guest_session_id == gid)
        .first()
    )
    if existing is not None:
        if existing.sealed:
            raise ValueError("guest_session_sealed")
        if locale:
            existing.locale = locale[:16]
        if timezone_name:
            existing.timezone_name = timezone_name[:64]
        # Re-issue secret so clients that only had session id (pre-claim era) can sync.
        # guest_session_id is already a bearer capability for symbol reveals.
        secret = _new_token()
        existing.session_secret_hash = _hash_secret(secret)
        existing.updated_at = utc_naive_now()
        db.add(existing)
        db.commit()
        return {
            "guest_session_id": gid,
            "session_secret": secret,
            "created": False,
            "sealed": bool(existing.sealed),
        }

    secret = _new_token()
    row = db_models.GuestSession(
        guest_session_id=gid,
        session_secret_hash=_hash_secret(secret),
        locale=(locale or "ru")[:16] if locale else "ru",
        timezone_name=(timezone_name or "UTC")[:64] if timezone_name else "UTC",
        sealed=False,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        again = (
            db.query(db_models.GuestSession)
            .filter(db_models.GuestSession.guest_session_id == gid)
            .first()
        )
        if again is None:
            raise
        return {
            "guest_session_id": gid,
            "session_secret": None,
            "created": False,
            "sealed": bool(again.sealed),
        }
    return {
        "guest_session_id": gid,
        "session_secret": secret,
        "created": True,
        "sealed": False,
    }


def _require_open_session(db: Session, guest_session_id: str, session_secret: str) -> db_models.GuestSession:
    gid = (guest_session_id or "").strip()
    secret = (session_secret or "").strip()
    if not gid or not secret:
        raise ValueError("guest_auth_required")
    row = (
        db.query(db_models.GuestSession)
        .filter(db_models.GuestSession.guest_session_id == gid)
        .first()
    )
    if row is None:
        raise ValueError("unknown_guest_session")
    if row.sealed or row.claimed_at is not None:
        raise ValueError("guest_session_sealed")
    if row.session_secret_hash != _hash_secret(secret):
        raise ValueError("invalid_guest_secret")
    return row


def upsert_guest_progress(
    db: Session,
    *,
    guest_session_id: str,
    session_secret: str,
    local_date: date,
    timezone_name: str = "UTC",
    locale: str = "ru",
    mood: dict | None = None,
    goals: dict | None = None,
    onboarding: dict | None = None,
    first_result: dict | None = None,
    ritual: dict | None = None,
    today_state: dict | None = None,
    day_story: dict | None = None,
    story_fingerprint: str | None = None,
    story_status: str | None = None,
    profile_draft: dict | None = None,
) -> dict[str, Any]:
    """Server write of guest progress. Does not accept reveal identities as source of truth for symbols."""
    session = _require_open_session(db, guest_session_id, session_secret)
    session.timezone_name = (timezone_name or session.timezone_name or "UTC")[:64]
    session.locale = (locale or session.locale or "ru")[:16]
    session.updated_at = utc_naive_now()
    db.add(session)

    snap = (
        db.query(db_models.GuestDaySnapshot)
        .filter(
            db_models.GuestDaySnapshot.guest_session_id == guest_session_id,
            db_models.GuestDaySnapshot.local_date == local_date,
        )
        .first()
    )
    if snap is None:
        snap = db_models.GuestDaySnapshot(
            guest_session_id=guest_session_id,
            local_date=local_date,
            timezone_name=(timezone_name or "UTC")[:64],
            locale=(locale or "ru")[:16],
        )
    else:
        snap.timezone_name = (timezone_name or snap.timezone_name or "UTC")[:64]
        snap.locale = (locale or snap.locale or "ru")[:16]

    def _merge(field: str, value: dict | None) -> None:
        if value is None:
            return
        if not isinstance(value, dict):
            return
        setattr(snap, field, value)

    _merge("mood", mood)
    _merge("goals", goals)
    _merge("onboarding", onboarding)
    _merge("first_result", first_result)
    _merge("ritual", ritual)
    _merge("today_state", today_state)
    if day_story is not None and isinstance(day_story, dict):
        snap.day_story = day_story
    if story_fingerprint is not None:
        snap.story_fingerprint = str(story_fingerprint)[:64]
    if story_status is not None:
        snap.story_status = str(story_status)[:32]
    if profile_draft is not None and isinstance(profile_draft, dict):
        # Strip anything that looks like secrets
        safe = {
            k: v
            for k, v in profile_draft.items()
            if k
            in (
                "first_name",
                "birth_date",
                "sun_sign",
                "life_path",
                "location_name",
                "latitude",
                "longitude",
                "birth_time",
                "time_unknown",
                "preview_seen_at",
                "first_today_started_at",
                "save_ready_at",
            )
        }
        snap.profile_draft = safe
    snap.updated_at = utc_naive_now()
    db.add(snap)
    db.commit()
    db.refresh(snap)
    return {
        "guest_session_id": guest_session_id,
        "local_date": local_date.isoformat(),
        "updated": True,
    }


def issue_claim_token(
    db: Session,
    *,
    guest_session_id: str,
    session_secret: str,
) -> dict[str, Any]:
    session = _require_open_session(db, guest_session_id, session_secret)
    token = _new_token()
    nonce = secrets.token_hex(8)
    session.claim_token_hash = _hash_secret(token)
    session.claim_token_expires_at = utc_naive_now() + CLAIM_TOKEN_TTL
    session.claim_nonce = nonce
    session.updated_at = utc_naive_now()
    db.add(session)
    db.commit()
    return {
        "claim_token": token,
        "expires_at": session.claim_token_expires_at.isoformat() + "Z",
        "nonce": nonce,
        "guest_session_id": guest_session_id,
    }


def _resolve_session_by_claim_token(db: Session, claim_token: str) -> db_models.GuestSession:
    token = (claim_token or "").strip()
    if not token:
        raise ValueError("claim_token_required")
    token_hash = _hash_secret(token)
    row = (
        db.query(db_models.GuestSession)
        .filter(db_models.GuestSession.claim_token_hash == token_hash)
        .first()
    )
    if row is None:
        raise ValueError("invalid_claim_token")
    # Already claimed: allow resolve for idempotent retry (same token) until expiry.
    if row.sealed and row.claimed_user_id is not None:
        if row.claim_token_expires_at is not None and row.claim_token_expires_at < utc_naive_now():
            raise ValueError("claim_token_expired")
        return row
    if row.claim_token_expires_at is None or row.claim_token_expires_at < utc_naive_now():
        raise ValueError("claim_token_expired")
    return row


def _fill_mood(db: Session, *, user_id: int, local_date: date, mood: dict | None, conflicts: list) -> bool:
    if not mood or not isinstance(mood, dict):
        return False
    existing = (
        db.query(db_models.StateCheckIn)
        .filter(
            db_models.StateCheckIn.user_id == user_id,
            db_models.StateCheckIn.checkin_date == local_date,
            db_models.StateCheckIn.phase == "morning",
        )
        .first()
    )
    scale = mood.get("mood_scale")
    if scale is None and isinstance(mood.get("mood"), (int, float)):
        scale = int(mood["mood"])
    tags = {"guest_mood": mood.get("mood") or mood.get("morning_mood_id")}
    if existing is not None:
        if existing.mood_scale is not None:
            conflicts.append({"block": "mood", "reason": "user_mood_present"})
            return False
        existing.mood_scale = int(scale) if scale is not None else existing.mood_scale
        existing.tags = {**(existing.tags or {}), **{k: v for k, v in tags.items() if v}}
        db.add(existing)
        return True
    row = db_models.StateCheckIn(
        user_id=user_id,
        checkin_date=local_date,
        phase="morning",
        mood_scale=int(scale) if scale is not None else None,
        tags={k: v for k, v in tags.items() if v},
    )
    db.add(row)
    return True


def _fill_goals(db: Session, *, user_id: int, local_date: date, goals: dict | None, conflicts: list) -> bool:
    if not goals or not isinstance(goals, dict):
        return False
    text = str(goals.get("day_goal") or "").strip()
    if not text and isinstance(goals.get("goals"), list) and goals["goals"]:
        text = str(goals["goals"][0]).strip()
    if not text:
        return False
    existing = (
        db.query(db_models.DailyGoalSnapshot)
        .filter(
            db_models.DailyGoalSnapshot.user_id == user_id,
            db_models.DailyGoalSnapshot.target_date == local_date,
        )
        .first()
    )
    if existing is not None and str(existing.goal_text or "").strip():
        conflicts.append({"block": "goals", "reason": "user_goal_present"})
        return False
    if existing is None:
        db.add(
            db_models.DailyGoalSnapshot(
                user_id=user_id, target_date=local_date, goal_text=text[:2000]
            )
        )
    else:
        existing.goal_text = text[:2000]
        db.add(existing)
    return True


def _fill_day_connection(
    db: Session,
    *,
    user_id: int,
    local_date: date,
    ritual: dict | None,
    today_state: dict | None,
    onboarding: dict | None,
    conflicts: list,
) -> bool:
    ritual = ritual if isinstance(ritual, dict) else {}
    today_state = today_state if isinstance(today_state, dict) else {}
    onboarding = onboarding if isinstance(onboarding, dict) else {}
    existing = (
        db.query(db_models.DayConnection)
        .filter(
            db_models.DayConnection.user_id == user_id,
            db_models.DayConnection.date == local_date,
        )
        .first()
    )
    focus = (
        str(ritual.get("headTopic") or today_state.get("focusTopicId") or "").strip() or None
    )
    intention = str(today_state.get("dayGoal") or "").strip() or None
    morning_done = bool(ritual.get("opened") or today_state.get("todayOpened") or ritual.get("checkInSubmitted"))
    if existing is None:
        db.add(
            db_models.DayConnection(
                user_id=user_id,
                date=local_date,
                morning_intention=intention,
                morning_focus=(focus or "")[:100] if focus else None,
                morning_completed=morning_done,
                question_of_day_answer=str(onboarding.get("intent_theme") or "")[:120] or None,
            )
        )
        return True
    changed = False
    if not (existing.morning_intention or "").strip() and intention:
        existing.morning_intention = intention
        changed = True
    elif (existing.morning_intention or "").strip() and intention:
        conflicts.append({"block": "day_connection", "reason": "user_intention_present"})
    if not (existing.morning_focus or "").strip() and focus:
        existing.morning_focus = focus[:100]
        changed = True
    if morning_done and not existing.morning_completed:
        existing.morning_completed = True
        changed = True
    if changed:
        existing.updated_at = utc_naive_now()
        db.add(existing)
    return changed


def _fill_locale(db: Session, *, user_id: int, locale: str | None, conflicts: list) -> bool:
    if not locale:
        return False
    settings = (
        db.query(db_models.UserSettings)
        .filter(db_models.UserSettings.user_id == user_id)
        .first()
    )
    if settings is None:
        db.add(
            db_models.UserSettings(
                user_id=user_id, locale=locale[:16], language=locale[:16]
            )
        )
        return True
    if (settings.locale or settings.language or "").strip():
        conflicts.append({"block": "locale", "reason": "user_locale_present"})
        return False
    settings.locale = locale[:16]
    settings.language = locale[:16]
    db.add(settings)
    return True


def _transfer_day_story_state(
    db: Session,
    *,
    guest_session_id: str,
    user_id: int,
    local_date: date,
    snap: db_models.GuestDaySnapshot | None,
    conflicts: list,
) -> tuple[bool, str | None, bool]:
    """Merge DayStoryState + optional guest story snapshot. Returns (transferred, status, refresh_required)."""
    from todayflow_backend.services.day_story_fingerprint_v1 import (
        compute_expected_day_story_fingerprint,
    )
    from todayflow_backend.services.day_story_refresh_v1 import (
        ensure_story_state,
        get_story_state_row,
    )

    gkey = owner_key_for_guest(guest_session_id)
    ukey = owner_key_for_user(user_id)
    grow = get_story_state_row(db, owner_key=gkey, local_date=local_date)
    urow = get_story_state_row(db, owner_key=ukey, local_date=local_date)

    guest_fp = grow.fingerprint if grow is not None else None
    guest_log_id = grow.last_generation_log_id if grow is not None else None
    guest_story = None
    if snap is not None:
        guest_fp = guest_fp or snap.story_fingerprint
        if isinstance(snap.day_story, dict):
            guest_story = snap.day_story

    if guest_story and isinstance(guest_story, dict) and guest_log_id is None:
        if guest_story.get("contract_version") == DAY_STORY_V1_CONTRACT or guest_story.get("story"):
            payload = (
                guest_story
                if guest_story.get("contract_version") == DAY_STORY_V1_CONTRACT
                else {"contract_version": DAY_STORY_V1_CONTRACT, **guest_story}
            )
            log = db_models.GenerationLog(
                user_id=user_id,
                module="day_story_v1",
                surface="day_story",
                status="success",
                used_fallback=True,
                locale=(snap.locale if snap else "ru"),
                input_payload={
                    "target_date": local_date.isoformat(),
                    "day_story_fingerprint": guest_fp,
                    "source": "guest_claim",
                },
                normalized_response=payload,
            )
            db.add(log)
            db.flush()
            guest_log_id = log.id

    transferred = False
    if grow is None and guest_log_id is None and guest_story is None:
        final = ensure_story_state(
            db, owner_key=ukey, local_date=local_date, user_id=user_id, commit=False
        )
        expected_fp, _ = compute_expected_day_story_fingerprint(
            db, user_id=user_id, owner_key=ukey, local_date=local_date
        )
        final.expected_fingerprint = expected_fp
        refresh_required = bool(final.fingerprint and final.fingerprint != expected_fp)
        if refresh_required:
            final.stale = True
        db.add(final)
        return False, ("stale" if refresh_required else "missing"), refresh_required

    if urow is None and grow is not None:
        grow.owner_key = ukey
        grow.user_id = user_id
        grow.guest_session_id = guest_session_id
        if guest_log_id:
            grow.last_generation_log_id = guest_log_id
        grow.updated_at = utc_naive_now()
        db.add(grow)
        transferred = True
    elif urow is None:
        db.add(
            db_models.DayStoryState(
                owner_key=ukey,
                user_id=user_id,
                guest_session_id=guest_session_id,
                local_date=local_date,
                timezone_name=(snap.timezone_name if snap else "UTC"),
                locale=(snap.locale if snap else "ru"),
                fingerprint=guest_fp,
                expected_fingerprint=guest_fp,
                stale=False,
                generation_seq=0,
                last_generation_log_id=guest_log_id,
            )
        )
        transferred = True
        if grow is not None:
            db.delete(grow)
    else:
        user_has = bool(urow.last_generation_log_id or urow.fingerprint)
        guest_has = bool(guest_log_id or guest_fp or guest_story)
        if user_has and guest_has:
            conflicts.append({"block": "day_story", "reason": "both_present_merge_stale"})
            if not urow.last_generation_log_id and guest_log_id:
                urow.last_generation_log_id = guest_log_id
            urow.stale = True
            urow.generation_seq = int(urow.generation_seq or 0) + 1
            db.add(urow)
            transferred = True
        elif not user_has and guest_has:
            urow.fingerprint = guest_fp
            urow.expected_fingerprint = guest_fp
            urow.last_generation_log_id = guest_log_id
            urow.stale = False
            db.add(urow)
            transferred = True
        if grow is not None:
            db.delete(grow)

    db.flush()
    expected_fp, _ = compute_expected_day_story_fingerprint(
        db, user_id=user_id, owner_key=ukey, local_date=local_date
    )
    final = get_story_state_row(db, owner_key=ukey, local_date=local_date)
    if final is None:
        final = ensure_story_state(
            db, owner_key=ukey, local_date=local_date, user_id=user_id, commit=False
        )
    final.expected_fingerprint = expected_fp
    refresh_required = bool(final.fingerprint != expected_fp)
    if refresh_required:
        final.stale = True
        final.generation_seq = int(final.generation_seq or 0) + 1
    else:
        final.stale = False
    db.add(final)
    status = "stale" if refresh_required else ("fresh" if final.fingerprint else "missing")
    return transferred, status, refresh_required


def _persist_first_result(
    db: Session, *, user_id: int, local_date: date, first_result: dict | None
) -> bool:
    if not first_result or not isinstance(first_result, dict):
        return False
    existing = (
        db.query(db_models.GenerationLog)
        .filter(
            db_models.GenerationLog.user_id == user_id,
            db_models.GenerationLog.module == "guest_claim_v1",
            db_models.GenerationLog.surface == "first_result",
        )
        .order_by(db_models.GenerationLog.created_at.desc())
        .first()
    )
    if existing is not None:
        ip = existing.input_payload if isinstance(existing.input_payload, dict) else {}
        if str(ip.get("target_date") or "") == local_date.isoformat():
            return False
    db.add(
        db_models.GenerationLog(
            user_id=user_id,
            module="guest_claim_v1",
            surface="first_result",
            status="success",
            used_fallback=False,
            input_payload={"target_date": local_date.isoformat(), "source": "guest_claim"},
            normalized_response=first_result,
        )
    )
    return True


_CLAIM_LOCKS: dict[str, Any] = {}
_CLAIM_LOCKS_GUARD = __import__("threading").Lock()


def _claim_lock(guest_session_id: str):
    import threading

    with _CLAIM_LOCKS_GUARD:
        lock = _CLAIM_LOCKS.get(guest_session_id)
        if lock is None:
            lock = threading.Lock()
            _CLAIM_LOCKS[guest_session_id] = lock
        return lock


def claim_guest_session_to_user(
    db: Session,
    *,
    claim_token: str,
    user_id: int,
    local_date: date | None = None,
    redirect_target: str = DEFAULT_REDIRECT,
) -> dict[str, Any]:
    """Atomic, idempotent claim. Frontend passes only claim_token."""
    # Resolve token first (outside lock) to get session id for lock key.
    session = _resolve_session_by_claim_token(db, claim_token)
    gid = session.guest_session_id
    lock = _claim_lock(gid)
    with lock:
        return _claim_guest_session_to_user_locked(
            db,
            claim_token=claim_token,
            user_id=user_id,
            local_date=local_date,
            redirect_target=redirect_target,
        )


def _claim_guest_session_to_user_locked(
    db: Session,
    *,
    claim_token: str,
    user_id: int,
    local_date: date | None = None,
    redirect_target: str = DEFAULT_REDIRECT,
) -> dict[str, Any]:
    session = _resolve_session_by_claim_token(db, claim_token)
    gid = session.guest_session_id

    # Idempotent: same user already claimed this guest session.
    prior = (
        db.query(db_models.GuestClaimRecord)
        .filter(
            db_models.GuestClaimRecord.guest_session_id == gid,
            db_models.GuestClaimRecord.user_id == user_id,
        )
        .first()
    )
    if prior is not None and prior.result_payload:
        return dict(prior.result_payload)

    if session.claimed_user_id is not None and int(session.claimed_user_id) != int(user_id):
        raise ValueError("guest_session_already_claimed")

    snaps = list(
        db.query(db_models.GuestDaySnapshot)
        .filter(db_models.GuestDaySnapshot.guest_session_id == gid)
        .all()
    )
    if local_date is not None:
        snaps = [s for s in snaps if s.local_date == local_date]
    if not snaps:
        primary_date = local_date or date.today()
        primary_snap = None
    else:
        primary_snap = sorted(snaps, key=lambda s: s.updated_at or s.created_at, reverse=True)[0]
        primary_date = primary_snap.local_date

    transferred: list[str] = []
    conflicts: list[dict[str, str]] = []
    story_status: str | None = None
    story_refresh_required = False

    try:
        # 1) Symbols (no inner commit)
        sym = claim_guest_symbols_to_user(
            db,
            guest_session_id=gid,
            user_id=user_id,
            local_date=primary_date if snaps else local_date,
            commit=False,
        )
        if int(sym.get("transferred_rows") or 0) > 0:
            transferred.append("symbols")

        # 2) Progress blocks from snapshots (canonical day = primary)
        if primary_snap is not None:
            if _fill_mood(db, user_id=user_id, local_date=primary_date, mood=primary_snap.mood, conflicts=conflicts):
                transferred.append("mood")
            if _fill_goals(db, user_id=user_id, local_date=primary_date, goals=primary_snap.goals, conflicts=conflicts):
                transferred.append("goals")
            if _fill_day_connection(
                db,
                user_id=user_id,
                local_date=primary_date,
                ritual=primary_snap.ritual,
                today_state=primary_snap.today_state,
                onboarding=primary_snap.onboarding,
                conflicts=conflicts,
            ):
                transferred.append("morning_ritual")
                transferred.append("today_state")
            if primary_snap.onboarding:
                transferred.append("onboarding")
            if _persist_first_result(
                db, user_id=user_id, local_date=primary_date, first_result=primary_snap.first_result
            ):
                transferred.append("first_result")
            if _fill_locale(db, user_id=user_id, locale=primary_snap.locale or session.locale, conflicts=conflicts):
                transferred.append("locale")

            ok_story, story_status, story_refresh_required = _transfer_day_story_state(
                db,
                guest_session_id=gid,
                user_id=user_id,
                local_date=primary_date,
                snap=primary_snap,
                conflicts=conflicts,
            )
            if ok_story:
                transferred.append("day_story")
            transferred.append("timezone")

        # Seal session (keep claim_token_hash until TTL for idempotent retries).
        session.claimed_at = utc_naive_now()
        session.claimed_user_id = user_id
        session.sealed = True
        session.updated_at = utc_naive_now()
        db.add(session)

        result = {
            "contract_version": GUEST_CLAIM_V1,
            "claim_status": "completed",
            "guest_session_id": gid,
            "user_id": user_id,
            "local_date": primary_date.isoformat(),
            "timezone_name": (primary_snap.timezone_name if primary_snap else session.timezone_name) or "UTC",
            "transferred_blocks": sorted(set(transferred)),
            "conflicts": conflicts,
            "story_status": story_status or "missing",
            "story_refresh_required": bool(story_refresh_required),
            "redirect_target": redirect_target or DEFAULT_REDIRECT,
        }

        record = db_models.GuestClaimRecord(
            guest_session_id=gid,
            user_id=user_id,
            local_date=primary_date,
            claim_status="completed",
            transferred_blocks=result["transferred_blocks"],
            conflicts=conflicts,
            story_status=result["story_status"],
            story_refresh_required=bool(story_refresh_required),
            redirect_target=result["redirect_target"],
            result_payload=result,
        )
        db.add(record)
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


def guest_session_is_mutable(db: Session, guest_session_id: str) -> bool:
    row = (
        db.query(db_models.GuestSession)
        .filter(db_models.GuestSession.guest_session_id == guest_session_id)
        .first()
    )
    if row is None:
        return True  # symbols API may create owner_key before session row
    return not bool(row.sealed)
