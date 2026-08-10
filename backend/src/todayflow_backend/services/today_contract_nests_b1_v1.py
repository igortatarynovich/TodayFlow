"""Wave B1 P0 nests on today_contract_v1: welcome_glass · today_progress · color_guide.

Canon: docs/today/TODAY_MAKE_YOURS_AND_WELCOME_SOT.md
Fill-empty / omit-empty only — never invent calm or product copy.
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Any, Iterable

from sqlalchemy.orm import Session

from todayflow_backend.db import models as db_models
from todayflow_backend.db.models import User

TODAY_PROGRESS_WINDOW_DAYS = 7

# Mirror FE buildHandoffWelcomeGlass VISUAL_MOOD_PILLS (todayHandoffWelcome.ts).
# Concrete cues — not abstract adjectives.
VISUAL_MOOD_TAGS: dict[str, tuple[str, str]] = {
    "grounded": ("Опора в теле", "Медленный надёжный темп"),
    "flow": ("Мягкая чувствительность", "Идти по течению"),
    "radiance": ("Проявить себя", "Открытый контакт"),
    "momentum": ("Импульс вперёд", "Решительный шаг"),
    "clarity": ("Ясный ум", "Порядок в делах"),
    "tension": ("Острое внимание", "Защитить фокус"),
    "renewal": ("Сбросить лишнее", "Место для нового"),
    "depth": ("Тишина внутри", "Без срочных решений"),
}

KIND_LABEL_RU: dict[str, str] = {
    "habit": "Привычка",
    "ascetic": "Аскеза",
    "practice": "Практика",
}

_GOOD_FOR_MAX_CHARS = 18
_GOOD_FOR_MAX = 3


def _clean(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _first_sentence(text: str) -> str:
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", text) if p.strip()]
    return parts[0] if parts else text


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def build_welcome_glass_v1(
    *,
    visual_mode: str | None = None,
    lunar_name: str | None = None,
    lunar_themes: str | None = None,
    lunar_guidance: str | None = None,
    do_items: Iterable[Any] | None = None,
) -> dict[str, Any]:
    """welcome_glass: { mood_tags[≤2], reason|null, good_for[≤3] }."""
    mode = _clean(visual_mode)
    mood_tags: list[str] = list(VISUAL_MOOD_TAGS[mode]) if mode in VISUAL_MOOD_TAGS else []

    name = _clean(lunar_name)
    themes = _clean(lunar_themes)
    guidance = _clean(lunar_guidance)
    reason: str | None = None
    if name and (themes or guidance):
        detail = _first_sentence(themes or guidance)
        reason = detail if name.lower() in detail.lower() else f"{name} — {detail}"
    elif name:
        reason = name
    elif themes or guidance:
        reason = _first_sentence(themes or guidance)
    if reason == "":
        reason = None

    good_for: list[str] = []
    seen: set[str] = set()
    for raw in do_items or ():
        line = _clean(raw)
        if not line or len(line) > _GOOD_FOR_MAX_CHARS:
            continue
        key = line.lower()
        if key in seen:
            continue
        seen.add(key)
        good_for.append(line)
        if len(good_for) >= _GOOD_FOR_MAX:
            break

    return {
        "mood_tags": mood_tags[:2],
        "reason": reason,
        "good_for": good_for,
    }


def lunar_fields_from_morning(morning: Any) -> tuple[str | None, str | None, str | None]:
    """Extract lunar name/themes/guidance from morning celestial_events (no invent)."""
    ce = getattr(morning, "celestial_events", None)
    if not isinstance(ce, dict):
        ce = _as_dict(ce)
    lunar = _as_dict(ce.get("lunar_phase"))
    name = _clean(lunar.get("name") or lunar.get("phase_name")) or None
    themes = _clean(lunar.get("themes")) or None
    guidance = _clean(lunar.get("guidance")) or None
    return name, themes, guidance


def lunar_fields_from_day_story(day_story: dict[str, Any] | None) -> tuple[str | None, str | None, str | None]:
    """Fallback lunar from day_foundation when morning nest missing."""
    story = _as_dict(day_story)
    foundation = _as_dict(story.get("day_foundation"))
    lunar = _as_dict(foundation.get("lunar"))
    phase = _as_dict(lunar.get("phase"))
    name = _clean(phase.get("name") or phase.get("phase_name")) or None
    themes = _clean(phase.get("themes")) or None
    guidance = _clean(phase.get("guidance")) or None
    return name, themes, guidance


def attach_welcome_glass_to_contract(
    contract: dict[str, Any],
    *,
    morning: Any | None = None,
) -> dict[str, Any]:
    """Fill welcome_glass on contract dict (mutates and returns)."""
    out = contract if isinstance(contract, dict) else {}
    atmosphere = _as_dict(out.get("day_atmosphere"))
    day_story = _as_dict(out.get("day_story"))
    do_items = day_story.get("do") if isinstance(day_story.get("do"), list) else []

    lunar_name = lunar_themes = lunar_guidance = None
    if morning is not None:
        lunar_name, lunar_themes, lunar_guidance = lunar_fields_from_morning(morning)
    if not (lunar_name or lunar_themes or lunar_guidance):
        lunar_name, lunar_themes, lunar_guidance = lunar_fields_from_day_story(day_story)

    out["welcome_glass"] = build_welcome_glass_v1(
        visual_mode=str(atmosphere.get("visual_mode") or "") or None,
        lunar_name=lunar_name,
        lunar_themes=lunar_themes,
        lunar_guidance=lunar_guidance,
        do_items=do_items,
    )
    return out


def build_color_guide_v1(
    *,
    day_story: dict[str, Any] | None = None,
    target_month: int | None = None,
) -> dict[str, Any] | None:
    """color_guide nest — fill-empty from props.color / talisman / catalog. Null if no name."""
    from todayflow_backend.services.day_color_catalog_v1 import (
        get_color_entry,
        resolve_seasonal_apply,
        sanitize_color_display_name,
    )

    story = _as_dict(day_story)
    scenario = _as_dict(story.get("day_scenario"))
    props = _as_dict(scenario.get("props"))
    color_prop = _as_dict(props.get("color"))
    avoid_prop = _as_dict(props.get("avoid_color"))
    talisman = _as_dict(story.get("talisman"))
    where = _as_dict(color_prop.get("where_to_use"))

    name = sanitize_color_display_name(
        _clean(color_prop.get("name")) or _clean(talisman.get("color"))
    )
    if not name:
        return None

    intensity = _clean(color_prop.get("intensity")) or None
    clothing = _clean(where.get("clothing")) or None
    accessory = _clean(where.get("accessory")) or None
    amount: str | None = None
    avoid = sanitize_color_display_name(
        _clean(avoid_prop.get("name")) or _clean(talisman.get("avoid_color"))
    ) or None
    avoid_why = _clean(avoid_prop.get("why")) or _clean(talisman.get("avoid_why")) or None

    # Catalog fill-empty only (never overwrite scenario/talisman).
    entry = get_color_entry(name)
    if entry:
        apply = resolve_seasonal_apply(_as_dict(entry.get("apply")), month=target_month)
        if not intensity:
            intensity = _clean(entry.get("intensity_default")) or None
        if not clothing:
            clothing = _clean(apply.get("clothing")) or None
        if not accessory:
            accessory = _clean(apply.get("accessory")) or None
        if not amount:
            amount = _clean(entry.get("intensity_default")) or None
        if not avoid:
            candidates = list(entry.get("avoid_candidates") or ())
            first = candidates[0] if candidates and isinstance(candidates[0], dict) else {}
            avoid = sanitize_color_display_name(_clean(first.get("name"))) or None
            if not avoid_why:
                avoid_why = _clean(first.get("why")) or None

    out: dict[str, Any] = {"name": name}
    if intensity:
        out["intensity"] = intensity
    if clothing:
        out["clothing"] = clothing
    if accessory:
        out["accessory"] = accessory
    if amount:
        out["amount"] = amount
    if avoid:
        out["avoid"] = avoid
    if avoid_why:
        out["avoid_why"] = avoid_why
    return out


def attach_color_guide_to_contract(
    contract: dict[str, Any],
    *,
    target_date: date | None = None,
) -> dict[str, Any]:
    out = contract if isinstance(contract, dict) else {}
    month = target_date.month if isinstance(target_date, date) else None
    guide = build_color_guide_v1(day_story=_as_dict(out.get("day_story")), target_month=month)
    out["color_guide"] = guide
    return out


def _window_dates(today: date, window_days: int = TODAY_PROGRESS_WINDOW_DAYS) -> list[date]:
    start = today - timedelta(days=window_days - 1)
    return [start + timedelta(days=i) for i in range(window_days)]


def _days_bool(today: date, completed: set[str], window_days: int = TODAY_PROGRESS_WINDOW_DAYS) -> list[bool]:
    return [d.isoformat() in completed for d in _window_dates(today, window_days)]


def _habit_streak(completed_dates: set[date], today: date) -> int:
    streak = 0
    cursor = today
    while cursor in completed_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def _match_ascetic_track(
    tracks: list[dict[str, Any]],
    *,
    title: str,
    asceticism_id: str | None,
) -> dict[str, Any] | None:
    if asceticism_id:
        by_id = next((t for t in tracks if t.get("asceticism_id") == asceticism_id), None)
        if by_id:
            return by_id
    title_clean = title.strip()
    by_title = next((t for t in tracks if _clean(t.get("title")) == title_clean), None)
    if by_title:
        return by_title
    prefix = title_clean[:12]
    if prefix:
        fuzzy = next((t for t in tracks if prefix in _clean(t.get("title"))), None)
        if fuzzy:
            return fuzzy
    return tracks[0] if tracks else None


def build_today_progress_v1(
    db: Session,
    *,
    user: User,
    target_date: date,
) -> dict[str, Any]:
    """Aggregate habit / ascetic / practice rows — mirror FE loadTodayGrowthTrackers."""
    from_date = target_date - timedelta(days=TODAY_PROGRESS_WINDOW_DAYS - 1)
    rows: list[dict[str, Any]] = []

    # --- Habit (first active) ---
    habit = (
        db.query(db_models.Habit)
        .filter(db_models.Habit.user_id == user.id, db_models.Habit.is_active.is_(True))
        .order_by(db_models.Habit.created_at.desc())
        .first()
    )
    if habit is not None:
        entries = (
            db.query(db_models.HabitEntry)
            .filter(
                db_models.HabitEntry.user_id == user.id,
                db_models.HabitEntry.habit_id == habit.id,
                db_models.HabitEntry.date >= from_date,
                db_models.HabitEntry.date <= target_date,
                db_models.HabitEntry.completed.is_(True),
            )
            .all()
        )
        completed_iso = {e.date.isoformat() for e in entries}
        # Streak may extend before window — query back a bit further for streak only.
        streak_entries = (
            db.query(db_models.HabitEntry)
            .filter(
                db_models.HabitEntry.user_id == user.id,
                db_models.HabitEntry.habit_id == habit.id,
                db_models.HabitEntry.date >= target_date - timedelta(days=89),
                db_models.HabitEntry.date <= target_date,
                db_models.HabitEntry.completed.is_(True),
            )
            .all()
        )
        streak_dates = {e.date for e in streak_entries}
        rows.append(
            {
                "id": f"habit:{habit.id}",
                "kind": "habit",
                "kind_label": KIND_LABEL_RU["habit"],
                "name": habit.name,
                "streak_days": _habit_streak(streak_dates, target_date),
                "days_bool": _days_bool(target_date, completed_iso),
            }
        )

    # --- Ascetic (first active contract) ---
    contract = (
        db.query(db_models.AsceticContract)
        .filter(
            db_models.AsceticContract.user_id == user.id,
            db_models.AsceticContract.status == "active",
        )
        .order_by(db_models.AsceticContract.created_at.desc())
        .first()
    )
    if contract is not None:
        progress_entries = (
            db.query(db_models.ProgressTrackerEntry)
            .filter(
                db_models.ProgressTrackerEntry.user_id == user.id,
                db_models.ProgressTrackerEntry.date >= from_date,
                db_models.ProgressTrackerEntry.date <= target_date,
                db_models.ProgressTrackerEntry.asceticism_id.isnot(None),
            )
            .all()
        )
        by_asc: dict[str, list[dict[str, Any]]] = {}
        for entry in progress_entries:
            aid = str(entry.asceticism_id or "")
            by_asc.setdefault(aid, []).append(
                {"date": entry.date.isoformat(), "completed": bool(entry.completed)}
            )
        all_contracts = (
            db.query(db_models.AsceticContract)
            .filter(db_models.AsceticContract.user_id == user.id)
            .all()
        )
        title_by_asc = {c.asceticism_id: c.title for c in all_contracts if c.asceticism_id}
        tracks = [
            {
                "asceticism_id": aid,
                "title": title_by_asc.get(aid),
                "entries": ents,
            }
            for aid, ents in by_asc.items()
        ]
        # Ensure active contract track exists even with no entries.
        if contract.asceticism_id and contract.asceticism_id not in by_asc:
            tracks.append(
                {
                    "asceticism_id": contract.asceticism_id,
                    "title": contract.title,
                    "entries": [],
                }
            )
        track = _match_ascetic_track(
            tracks,
            title=str(contract.title or ""),
            asceticism_id=contract.asceticism_id,
        )
        ascetic_completed: set[str] = set()
        if track:
            for ent in track.get("entries") or []:
                if ent.get("completed"):
                    ascetic_completed.add(str(ent.get("date") or ""))
        if contract.last_completed_date and contract.last_completed_date == target_date:
            ascetic_completed.add(target_date.isoformat())
        rows.append(
            {
                "id": f"ascetic:{contract.id}",
                "kind": "ascetic",
                "kind_label": KIND_LABEL_RU["ascetic"],
                "name": contract.title,
                "streak_days": max(0, int(contract.streak_days or 0)),
                "days_bool": _days_bool(target_date, ascetic_completed),
            }
        )

    # --- Practice ---
    usages = (
        db.query(db_models.PracticeUsage)
        .filter(db_models.PracticeUsage.user_id == user.id)
        .order_by(db_models.PracticeUsage.completed_at.desc())
        .limit(40)
        .all()
    )
    practice_completed: set[str] = set()
    for usage in usages:
        if usage.completed_at is None:
            continue
        practice_completed.add(usage.completed_at.date().isoformat())

    # Streak logic mirrors /practices/progress
    if usages:
        dates = sorted({u.completed_at.date() for u in usages if u.completed_at}, reverse=True)
        current_streak = 0
        today = target_date
        yesterday = today - timedelta(days=1)
        if dates and dates[0] == today:
            current_streak = 1
            for i in range(1, len(dates)):
                if dates[i] == today - timedelta(days=i):
                    current_streak += 1
                else:
                    break
        elif dates and dates[0] == yesterday:
            current_streak = 1
            for i in range(1, len(dates)):
                if dates[i] == yesterday - timedelta(days=i):
                    current_streak += 1
                else:
                    break
    else:
        current_streak = 0

    practice_name: str | None = None
    practice_id: str | None = None
    try:
        from todayflow_backend.api.practices import GENERAL_PRACTICES, PERSONALIZED_PRACTICES

        all_practices = {p["id"]: p for p in GENERAL_PRACTICES + PERSONALIZED_PRACTICES}
        if usages:
            latest = usages[0]
            practice_id = latest.practice_id
            practice_name = _clean((all_practices.get(latest.practice_id) or {}).get("title")) or None
        if not practice_name and GENERAL_PRACTICES:
            practice_id = str(GENERAL_PRACTICES[0].get("id") or "") or None
            practice_name = _clean(GENERAL_PRACTICES[0].get("title")) or None
    except Exception:
        practice_name = None
        practice_id = None

    include_practice = bool(practice_name) and (
        current_streak > 0 or bool(practice_completed) or bool(practice_id)
    )
    if include_practice and practice_name:
        rows.append(
            {
                "id": "practice",
                "kind": "practice",
                "kind_label": KIND_LABEL_RU["practice"],
                "name": practice_name,
                "streak_days": max(0, current_streak),
                "days_bool": _days_bool(target_date, practice_completed),
            }
        )

    return {"rows": rows}


def attach_today_progress_to_contract(
    contract: dict[str, Any],
    db: Session,
    *,
    user: User,
    target_date: date,
) -> dict[str, Any]:
    out = contract if isinstance(contract, dict) else {}
    try:
        out["today_progress"] = build_today_progress_v1(db, user=user, target_date=target_date)
    except Exception:
        out["today_progress"] = {"rows": []}
    return out


def attach_b1_nests_to_contract(
    contract: dict[str, Any],
    *,
    morning: Any | None = None,
    db: Session | None = None,
    user: User | None = None,
    target_date: date | None = None,
) -> dict[str, Any]:
    """Attach all Wave B1 nests. today_progress requires db+user."""
    out = attach_welcome_glass_to_contract(contract, morning=morning)
    out = attach_color_guide_to_contract(out, target_date=target_date)
    if db is not None and user is not None and target_date is not None:
        out = attach_today_progress_to_contract(out, db, user=user, target_date=target_date)
    else:
        out.setdefault("today_progress", {"rows": []})
    return out
