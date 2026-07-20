"""Day story refresh: fingerprint, stale mark, locked rebuild (no LLM inside reveal)."""

from __future__ import annotations

import logging
import threading
from datetime import date
from typing import Any, Callable

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from todayflow_backend.db import models as db_models
from todayflow_backend.db.models import User, utc_naive_now
from todayflow_backend.services.day_story_fingerprint_v1 import (
    compute_expected_day_story_fingerprint,
)
from todayflow_backend.services.day_symbol_state_v1 import owner_key_for_guest, owner_key_for_user

logger = logging.getLogger(__name__)

_LOCKS: dict[str, threading.Lock] = {}
_LOCKS_GUARD = threading.Lock()


def _lock_for(owner_key: str, local_date: date) -> threading.Lock:
    key = f"{owner_key}:{local_date.isoformat()}"
    with _LOCKS_GUARD:
        lock = _LOCKS.get(key)
        if lock is None:
            lock = threading.Lock()
            _LOCKS[key] = lock
        return lock


def get_story_state_row(
    db: Session, *, owner_key: str, local_date: date
) -> db_models.DayStoryState | None:
    return (
        db.query(db_models.DayStoryState)
        .filter(
            db_models.DayStoryState.owner_key == owner_key,
            db_models.DayStoryState.local_date == local_date,
        )
        .first()
    )


def ensure_story_state(
    db: Session,
    *,
    owner_key: str,
    local_date: date,
    timezone_name: str = "UTC",
    locale: str = "ru",
    user_id: int | None = None,
    guest_session_id: str | None = None,
    commit: bool = True,
) -> db_models.DayStoryState:
    row = get_story_state_row(db, owner_key=owner_key, local_date=local_date)
    if row is not None:
        return row
    row = db_models.DayStoryState(
        owner_key=owner_key,
        user_id=user_id,
        guest_session_id=guest_session_id,
        local_date=local_date,
        timezone_name=(timezone_name or "UTC")[:64],
        locale=(locale or "ru")[:16],
        stale=False,
        generation_seq=0,
    )
    db.add(row)
    if not commit:
        db.flush()
        return row
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        existing = get_story_state_row(db, owner_key=owner_key, local_date=local_date)
        if existing is None:
            raise
        return existing
    return row


def mark_day_story_stale_after_input_change(
    db: Session,
    *,
    owner_key: str,
    local_date: date,
    timezone_name: str = "UTC",
    locale: str = "ru",
    user_id: int | None = None,
    guest_session_id: str | None = None,
) -> dict[str, Any]:
    """Compare expected fingerprint to last valid; mark stale if different. No LLM."""
    expected_fp, _payload = compute_expected_day_story_fingerprint(
        db,
        user_id=user_id,
        owner_key=owner_key,
        local_date=local_date,
        timezone_name=timezone_name,
        locale=locale,
    )
    row = ensure_story_state(
        db,
        owner_key=owner_key,
        local_date=local_date,
        timezone_name=timezone_name,
        locale=locale,
        user_id=user_id,
        guest_session_id=guest_session_id,
    )
    row.expected_fingerprint = expected_fp
    row.timezone_name = (timezone_name or row.timezone_name or "UTC")[:64]
    row.locale = (locale or row.locale or "ru")[:16]
    refresh_required = bool(row.fingerprint != expected_fp)
    if refresh_required:
        row.stale = True
        row.generation_seq = int(row.generation_seq or 0) + 1
    else:
        row.stale = False
    row.updated_at = utc_naive_now()
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "story_refresh_required": refresh_required,
        "story_status": "stale" if refresh_required else "fresh",
        "story_fingerprint": expected_fp,
        "story_generation_seq": int(row.generation_seq or 0),
    }


def attach_story_refresh_meta(view: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
    out = dict(view)
    out.update(meta)
    return out


def story_progress_meta(db: Session, *, owner_key: str, local_date: date) -> dict[str, Any]:
    row = get_story_state_row(db, owner_key=owner_key, local_date=local_date)
    if row is None:
        return {"story_status": "missing", "story_refresh_required": False}
    stale = bool(row.stale) or (
        row.fingerprint is not None
        and row.expected_fingerprint is not None
        and row.fingerprint != row.expected_fingerprint
    )
    return {
        "story_status": "stale" if stale else "fresh",
        "story_refresh_required": stale,
        "story_fingerprint": row.expected_fingerprint or row.fingerprint,
        "story_generation_seq": int(row.generation_seq or 0),
    }


def load_story_by_log_id(db: Session, generation_log_id: int | None) -> dict[str, Any] | None:
    if not generation_log_id:
        return None
    row = (
        db.query(db_models.GenerationLog)
        .filter(db_models.GenerationLog.id == int(generation_log_id))
        .first()
    )
    if row is None:
        return None
    nr = row.normalized_response if isinstance(row.normalized_response, dict) else None
    return nr


def refresh_day_story_for_user(
    db: Session,
    *,
    user: User,
    local_date: date,
    timezone_name: str,
    locale: str,
    build_fn: Callable[..., tuple[dict[str, Any], int, bool]],
    llm_calls: list | None = None,
    force: bool = False,
    max_attempts: int = 2,
) -> dict[str, Any]:
    """
    Rebuild day_story when fingerprint differs. Thread-locked per owner+date.

    build_fn(db, *, user, target_date, locale, force_rebuild, expected_fingerprint, fingerprint_payload)
      -> (story, generation_log_id, used_fallback)

    Slow/stale generations never overwrite a newer fingerprint: after each build we re-check
    expected fingerprint; mismatch → discard write and retry (bounded).
    """
    owner_key = owner_key_for_user(user.id)
    lock = _lock_for(owner_key, local_date)
    with lock:
        for attempt in range(max(1, int(max_attempts))):
            expected_fp, fp_payload = compute_expected_day_story_fingerprint(
                db,
                user_id=int(user.id),
                owner_key=owner_key,
                local_date=local_date,
                timezone_name=timezone_name,
                locale=locale,
            )
            state = ensure_story_state(
                db,
                owner_key=owner_key,
                local_date=local_date,
                timezone_name=timezone_name,
                locale=locale,
                user_id=int(user.id),
            )
            state.expected_fingerprint = expected_fp
            db.add(state)
            db.commit()
            db.refresh(state)

            if (
                not force
                and state.fingerprint == expected_fp
                and state.last_generation_log_id
                and not state.stale
            ):
                story = load_story_by_log_id(db, state.last_generation_log_id)
                if story is not None:
                    return {
                        "rebuilt": False,
                        "story_status": "fresh",
                        "story_fingerprint": expected_fp,
                        "story_refresh_required": False,
                        "generation_id": str(state.last_generation_log_id),
                        "story": story,
                        "fingerprint_payload": fp_payload,
                    }

            build_fp = expected_fp
            if llm_calls is not None:
                llm_calls.append(build_fp)

            try:
                story, gen_id, used_fallback = build_fn(
                    db,
                    user=user,
                    target_date=local_date,
                    locale=locale,
                    force_rebuild=True,
                    expected_fingerprint=build_fp,
                    fingerprint_payload=fp_payload,
                )
            except Exception as exc:
                logger.exception("day_story refresh LLM/build failed: %s", exc)
                db.refresh(state)
                last = load_story_by_log_id(db, state.last_generation_log_id)
                return {
                    "rebuilt": False,
                    "story_status": "error",
                    "story_refresh_required": True,
                    "story_fingerprint": expected_fp,
                    "generation_id": str(state.last_generation_log_id or ""),
                    "story": last,
                    "error": "day_story_refresh_failed",
                    "fingerprint_payload": fp_payload,
                }

            # Re-read expected fingerprint after build — newest inputs win.
            db.expire_all()
            current_expected, current_payload = compute_expected_day_story_fingerprint(
                db,
                user_id=int(user.id),
                owner_key=owner_key,
                local_date=local_date,
                timezone_name=timezone_name,
                locale=locale,
            )
            state = get_story_state_row(db, owner_key=owner_key, local_date=local_date)
            if state is None:
                state = ensure_story_state(
                    db,
                    owner_key=owner_key,
                    local_date=local_date,
                    timezone_name=timezone_name,
                    locale=locale,
                    user_id=int(user.id),
                )
            if current_expected != build_fp:
                # Newer inputs won — do not persist this generation as canonical.
                state.expected_fingerprint = current_expected
                state.stale = True
                db.add(state)
                db.commit()
                if attempt + 1 < max_attempts:
                    continue
                last = load_story_by_log_id(db, state.last_generation_log_id) or story
                return {
                    "rebuilt": True,
                    "story_status": "stale",
                    "story_refresh_required": True,
                    "story_fingerprint": current_expected,
                    "generation_id": str(state.last_generation_log_id or gen_id),
                    "story": last,
                    "used_fallback": used_fallback,
                    "note": "newer_fingerprint_pending",
                    "fingerprint_payload": current_payload,
                }

            state.fingerprint = build_fp
            state.expected_fingerprint = build_fp
            state.stale = False
            state.last_generation_log_id = int(gen_id)
            state.updated_at = utc_naive_now()
            db.add(state)
            db.commit()
            return {
                "rebuilt": True,
                "story_status": "fresh",
                "story_fingerprint": build_fp,
                "story_refresh_required": False,
                "generation_id": str(gen_id),
                "story": story,
                "used_fallback": used_fallback,
                "fingerprint_payload": fp_payload,
            }

        return {
            "rebuilt": False,
            "story_status": "error",
            "story_refresh_required": True,
            "story_fingerprint": None,
            "generation_id": "",
            "story": None,
            "error": "day_story_refresh_exhausted",
        }


def mark_stale_for_owner(
    db: Session,
    *,
    user_id: int | None = None,
    guest_session_id: str | None = None,
    local_date: date,
    timezone_name: str = "UTC",
    locale: str = "ru",
) -> dict[str, Any]:
    if user_id is not None:
        owner_key = owner_key_for_user(user_id)
        gid = None
    else:
        owner_key = owner_key_for_guest(guest_session_id or "")
        gid = guest_session_id
    return mark_day_story_stale_after_input_change(
        db,
        owner_key=owner_key,
        local_date=local_date,
        timezone_name=timezone_name,
        locale=locale,
        user_id=user_id,
        guest_session_id=gid,
    )
