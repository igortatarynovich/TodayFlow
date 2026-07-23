"""Stable day_story fingerprint — only inputs that actually change the text."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.core.llm_openai_compatible import (
    is_llm_chat_configured,
    resolve_default_chat_model,
)
from todayflow_backend.db import models as db_models
from todayflow_backend.services.day_story_v1 import DAY_STORY_PROMPT_VER, DAY_STORY_V1_CONTRACT
from todayflow_backend.services.day_symbol_state_v1 import (
    get_state_row,
    is_card_revealed,
    is_number_revealed,
    owner_key_for_user,
)
from todayflow_backend.services.today_narrative import _latest_snapshot_id

# Include model in the hash for storage parity; auto-regen on model bump is opt-in.
REGENERATE_ON_MODEL_CHANGE = False


def _stable_hash(payload: dict[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:32]


def resolve_story_model_id() -> str:
    if is_llm_chat_configured():
        return str(resolve_default_chat_model() or "configured")
    return "none"


def collect_mood_and_goals(db: Session, *, user_id: int | None, local_date: date) -> tuple[Any, list[str]]:
    if user_id is None:
        return None, []
    mood = None
    checkin = (
        db.query(db_models.StateCheckIn)
        .filter(
            db_models.StateCheckIn.user_id == user_id,
            db_models.StateCheckIn.checkin_date == local_date,
            db_models.StateCheckIn.phase == "morning",
        )
        .first()
    )
    if checkin is not None and checkin.mood_scale is not None:
        mood = int(checkin.mood_scale)
    goals: list[str] = []
    snap = (
        db.query(db_models.DailyGoalSnapshot)
        .filter(
            db_models.DailyGoalSnapshot.user_id == user_id,
            db_models.DailyGoalSnapshot.target_date == local_date,
        )
        .first()
    )
    if snap is not None and str(snap.goal_text or "").strip():
        goals = [str(snap.goal_text).strip()[:120]]
    if not goals:
        rows = (
            db.query(db_models.WeeklyGoal)
            .filter(
                db_models.WeeklyGoal.user_id == user_id,
                db_models.WeeklyGoal.completed.is_(False),
            )
            .order_by(db_models.WeeklyGoal.id.asc())
            .limit(8)
            .all()
        )
        goals = sorted(str(r.title or "").strip()[:120] for r in rows if str(r.title or "").strip())
    return mood, goals


def revealed_symbol_ids(
    db: Session,
    *,
    owner_key: str,
    local_date: date,
) -> tuple[int | None, int | None]:
    row = get_state_row(db, owner_key=owner_key, local_date=local_date)
    card_id: int | None = None
    number_value: int | None = None
    if is_card_revealed(row) and row is not None and row.card_id is not None:
        try:
            card_id = int(row.card_id)
        except (TypeError, ValueError):
            card_id = None
    if is_number_revealed(row) and row is not None and row.number_reduced is not None:
        number_value = int(row.number_reduced)
    return card_id, number_value


def build_fingerprint_payload(
    *,
    local_date: date,
    timezone_name: str,
    locale: str,
    mood: Any,
    goals: list[str],
    profile_snapshot_id: int | None,
    revealed_card_id: int | None,
    revealed_number: int | None,
    prompt_version: str = DAY_STORY_PROMPT_VER,
    model: str | None = None,
    contract_version: str = DAY_STORY_V1_CONTRACT,
    include_model: bool = True,
    sky_digest: str | None = None,
    color_name: str | None = None,
    stone_name: str | None = None,
) -> dict[str, Any]:
    model_id = model if model is not None else resolve_story_model_id()
    payload: dict[str, Any] = {
        "local_date": local_date.isoformat(),
        "timezone": (timezone_name or "UTC").strip() or "UTC",
        "locale": (locale or "ru").strip()[:32] or "ru",
        "mood": mood,
        "goals": list(goals or []),
        "profile_snapshot_id": profile_snapshot_id,
        "revealed_card_id": revealed_card_id,
        "revealed_number": revealed_number,
        "prompt_version": prompt_version,
        "contract_version": contract_version,
    }
    if sky_digest:
        payload["sky_digest"] = sky_digest
    if color_name:
        payload["color_name"] = str(color_name).strip()[:80]
    if stone_name:
        payload["stone_name"] = str(stone_name).strip()[:80]
    if include_model and (REGENERATE_ON_MODEL_CHANGE or True):
        # Always store model in fingerprint for parity; regeneration policy is enforced at refresh call sites.
        payload["model"] = model_id
    return payload


def _sky_digest_from_celestial(celestial_events: dict[str, Any] | None) -> str | None:
    ce = celestial_events if isinstance(celestial_events, dict) else {}
    if not ce:
        return None
    bits: list[str] = []
    lunar = ce.get("lunar_phase") if isinstance(ce.get("lunar_phase"), dict) else {}
    if lunar.get("name"):
        bits.append(f"moon:{lunar.get('name')}")
    for row in (ce.get("ingresses") or [])[:3]:
        if isinstance(row, dict) and row.get("planet"):
            bits.append(f"ing:{row.get('planet')}:{row.get('sign')}")
    for row in (ce.get("sky_aspects") or [])[:2]:
        if isinstance(row, dict) and row.get("id"):
            bits.append(f"asp:{row.get('id')}")
    for row in (ce.get("retrogrades") or [])[:2]:
        if isinstance(row, dict) and row.get("planet"):
            bits.append(f"ret:{row.get('planet')}")
    if not bits:
        return None
    return _stable_hash({"sky": bits})


def compute_day_story_fingerprint(payload: dict[str, Any]) -> str:
    return _stable_hash(payload)


def compute_expected_day_story_fingerprint(
    db: Session,
    *,
    user_id: int | None,
    owner_key: str | None = None,
    local_date: date,
    timezone_name: str = "UTC",
    locale: str = "ru",
    celestial_events: dict[str, Any] | None = None,
    color_name: str | None = None,
    stone_name: str | None = None,
) -> tuple[str, dict[str, Any]]:
    key = owner_key or (owner_key_for_user(user_id) if user_id is not None else "")
    if not key:
        raise ValueError("owner_key_or_user_required")
    card_id, number_value = revealed_symbol_ids(db, owner_key=key, local_date=local_date)
    mood, goals = collect_mood_and_goals(db, user_id=user_id, local_date=local_date)
    snapshot_id = _latest_snapshot_id(db, user_id) if user_id is not None else None
    payload = build_fingerprint_payload(
        local_date=local_date,
        timezone_name=timezone_name,
        locale=locale,
        mood=mood,
        goals=goals,
        profile_snapshot_id=snapshot_id,
        revealed_card_id=card_id,
        revealed_number=number_value,
        sky_digest=_sky_digest_from_celestial(celestial_events),
        color_name=color_name,
        stone_name=stone_name,
    )
    return compute_day_story_fingerprint(payload), payload
