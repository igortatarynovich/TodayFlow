"""Character continuity for Today — same CE hero, rotating day angle.

Canon: PROFILE_EXPERIENCE_SCENARIO_V1 §3.1
- Same identity_line + primary_tension every day
- day_angle rotates (mind|feelings|will|growth|presence|structure)
- Never invents a new character arc
"""

from __future__ import annotations

import hashlib
from datetime import date
from typing import Any, Final

DAY_ANGLE_IDS: Final[tuple[str, ...]] = (
    "mind",
    "feelings",
    "will",
    "growth",
    "presence",
    "structure",
)

_ANGLE_HINT_RU: Final[dict[str, str]] = {
    "mind": "Сегодня смотри ось через мышление и формулировки — как человек объясняет себе день.",
    "feelings": "Сегодня смотри ось через чувства и контакт — где тепло / дистанция.",
    "will": "Сегодня смотри ось через действие и удержание курса — старт, стоп, темп.",
    "growth": "Сегодня смотри ось через рост — где нужен сознательный шаг, а не автопилот.",
    "presence": "Сегодня смотри ось через первый контакт с миром — как человека считывают и как он входит.",
    "structure": "Сегодня смотри ось через быт и опору — режим, ресурсы, рутина.",
}

_ANGLE_HINT_EN: Final[dict[str, str]] = {
    "mind": "Today light the axis through thinking and wording — how they explain the day to themselves.",
    "feelings": "Today light the axis through feeling and contact — warmth vs distance.",
    "will": "Today light the axis through action and holding course — start, stop, pace.",
    "growth": "Today light the axis through growth — where a conscious step beats autopilot.",
    "presence": "Today light the axis through first contact — how they are read and how they enter.",
    "structure": "Today light the axis through daily structure — rhythm, resources, routine.",
}

CONTINUITY_VERSION: Final = "character_continuity_v0"


def _clip(value: Any, limit: int) -> str | None:
    text = " ".join(str(value or "").split()).strip()
    if not text:
        return None
    if len(text) > limit:
        return text[: limit - 1].rstrip() + "…"
    return text


def extract_primary_tension_text(snapshot_or_contract: dict[str, Any] | None) -> str | None:
    """Prefer Stage 3 primary_tension; fall back to contract recurring_patterns / inner_tension."""
    src = snapshot_or_contract if isinstance(snapshot_or_contract, dict) else {}
    diagnostics = src.get("diagnostics") if isinstance(src.get("diagnostics"), dict) else {}
    stage3 = diagnostics.get("character_engine_stage3")
    if isinstance(stage3, dict):
        nested = stage3.get("stage3") if isinstance(stage3.get("stage3"), dict) else stage3
        pt = nested.get("primary_tension") if isinstance(nested, dict) else None
        if isinstance(pt, dict):
            hit = _clip(pt.get("surface_text"), 420)
            if hit:
                return hit
    pc = src.get("profile_contract_v1") if isinstance(src.get("profile_contract_v1"), dict) else src
    if isinstance(pc, dict):
        patterns = pc.get("recurring_patterns")
        if isinstance(patterns, list) and patterns:
            hit = _clip(patterns[0], 420)
            if hit:
                return hit
        hit = _clip(pc.get("inner_tension"), 420)
        if hit:
            return hit
    return None


def select_day_character_angle_v0(
    *,
    target_date: date,
    identity_line: str | None = None,
    primary_tension: str | None = None,
    locale: str = "ru",
) -> dict[str, Any]:
    """Deterministic angle for the civil day — stable for same date + continuity strings."""
    en = (locale or "").strip().lower().startswith("en")
    seed = "|".join(
        [
            target_date.isoformat(),
            (identity_line or "").strip()[:120],
            (primary_tension or "").strip()[:160],
        ]
    )
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    idx = int(digest[:8], 16) % len(DAY_ANGLE_IDS)
    angle_id = DAY_ANGLE_IDS[idx]
    hints = _ANGLE_HINT_EN if en else _ANGLE_HINT_RU
    return {
        "id": angle_id,
        "hint": hints[angle_id],
        "selection": "sha256_mod_angles_v0",
    }


def build_character_continuity_v0(
    *,
    target_date: date,
    experience_slice: dict[str, Any] | None,
    core_profile: dict[str, Any] | None = None,
    locale: str = "ru",
) -> dict[str, Any] | None:
    """Layer for DayContext: same hero, rotating angle. None if no identity/tension at all."""
    exp = experience_slice if isinstance(experience_slice, dict) else {}
    identity = _clip(exp.get("identity_line"), 420)
    tension = _clip(exp.get("primary_tension"), 420)
    if not tension and isinstance(core_profile, dict):
        tension = extract_primary_tension_text(core_profile)
    if not identity and not tension:
        return None
    angle = select_day_character_angle_v0(
        target_date=target_date,
        identity_line=identity,
        primary_tension=tension,
        locale=locale,
    )
    en = (locale or "").strip().lower().startswith("en")
    rule = (
        "Same person every day: do not invent a new character. "
        "Re-light identity_line + primary_tension from today's day_angle only."
        if en
        else (
            "Тот же человек каждый день: не изобретай нового героя. "
            "Подсвети identity_line + primary_tension только через сегодняшний day_angle."
        )
    )
    out: dict[str, Any] = {
        "contract_version": CONTINUITY_VERSION,
        "rule": rule,
        "day_angle": angle["id"],
        "day_angle_hint": angle["hint"],
        "angle_selection": angle["selection"],
        "rewrites_identity": False,
    }
    if identity:
        out["identity_line"] = identity
    if tension:
        out["primary_tension"] = tension
    return out
