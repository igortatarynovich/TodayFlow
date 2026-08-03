"""Day Atmosphere v1 — deterministic mapper from day story → closed visual contract.

FOUNDATION_UI §11–§12. Engine output is never colors/CSS — only closed fields.
Maps thesis.mode (+ optional time-of-day) → visual_mode / intensity / contrast / decor.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

DAY_ATMOSPHERE_VERSION = "day_atmosphere_v1"

VISUAL_MODES = frozenset(
    {
        "grounded",
        "flow",
        "radiance",
        "momentum",
        "clarity",
        "tension",
        "renewal",
        "depth",
    }
)

DECOR_VARIANTS: dict[str, tuple[str, str]] = {
    "grounded": ("contour", "stones"),
    "flow": ("ripple", "current"),
    "radiance": ("rays", "bloom"),
    "momentum": ("diagonal", "trail"),
    "clarity": ("grid", "orbit"),
    "tension": ("fracture", "crossline"),
    "renewal": ("sprout", "horizon"),
    "depth": ("still", "drift"),
}

# thesis.mode → base visual_mode (before night/depth soft path)
_MODE_TO_VISUAL: dict[str, str] = {
    "stability": "grounded",
    "recovery": "renewal",
    "opportunity": "radiance",
    "transition": "flow",
    "conflict": "tension",
    "pressure": "tension",
    "change": "momentum",
}

_MODE_INTENSITY: dict[str, float] = {
    "stability": 0.32,
    "recovery": 0.36,
    "opportunity": 0.52,
    "transition": 0.48,
    "conflict": 0.72,
    "pressure": 0.7,
    "change": 0.66,
}

_MODE_CONTRAST: dict[str, str] = {
    "stability": "soft",
    "recovery": "soft",
    "opportunity": "medium",
    "transition": "medium",
    "conflict": "strong",
    "pressure": "strong",
    "change": "strong",
}

_MODE_WARMTH: dict[str, float] = {
    "stability": 0.62,
    "recovery": 0.55,
    "opportunity": 0.7,
    "transition": 0.45,
    "conflict": 0.35,
    "pressure": 0.3,
    "change": 0.55,
}


def time_phase_from_hour(hour: int | None) -> str:
    if hour is None:
        return "day"
    h = int(hour) % 24
    if 5 <= h < 11:
        return "morning"
    if 11 <= h < 17:
        return "day"
    if 17 <= h < 21:
        return "evening"
    return "night"


def _pick_decor(visual_mode: str, *, local_date: str | None, thesis_mode: str) -> str:
    pair = DECOR_VARIANTS.get(visual_mode) or DECOR_VARIANTS["clarity"]
    seed = f"{visual_mode}|{thesis_mode}|{local_date or ''}"
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return pair[int(digest[0], 16) % 2]


def map_thesis_mode_to_visual(
    thesis_mode: str | None,
    *,
    time_phase: str = "day",
) -> str:
    """Closed mapping — never returns an open string."""
    mode = (thesis_mode or "").strip().lower()
    base = _MODE_TO_VISUAL.get(mode)
    if not base:
        return "clarity"
    # Soft introspective night path → depth (FOUNDATION_UI plan)
    if time_phase in ("evening", "night") and mode in ("stability", "recovery"):
        return "depth"
    return base


def build_day_atmosphere_v1(
    *,
    day_thesis: dict[str, Any] | None = None,
    local_date: str | None = None,
    hour: int | None = None,
    time_phase: str | None = None,
) -> dict[str, Any]:
    """Build public nest for today_contract. Always returns a full closed dict."""
    thesis = day_thesis if isinstance(day_thesis, dict) else {}
    thesis_mode = str(thesis.get("mode") or "").strip().lower() or "stability"

    phase = (time_phase or "").strip().lower()
    if phase not in ("morning", "day", "evening", "night"):
        phase = time_phase_from_hour(hour if hour is not None else datetime.now().hour)

    visual_mode = map_thesis_mode_to_visual(thesis_mode, time_phase=phase)
    intensity = float(_MODE_INTENSITY.get(thesis_mode, 0.4))
    warmth = float(_MODE_WARMTH.get(thesis_mode, 0.5))
    contrast = _MODE_CONTRAST.get(thesis_mode, "medium")
    motion = "none" if visual_mode in ("depth", "grounded") and intensity < 0.4 else "low"
    decor = _pick_decor(visual_mode, local_date=local_date, thesis_mode=thesis_mode)

    return {
        "version": DAY_ATMOSPHERE_VERSION,
        "visual_mode": visual_mode,
        "intensity": intensity,
        "warmth": warmth,
        "motion": motion,
        "contrast": contrast,
        "decor_variant": decor,
        "time_phase": phase,
    }


def day_atmosphere_from_story(
    story: dict[str, Any] | None,
    *,
    local_date: str | None = None,
    hour: int | None = None,
) -> dict[str, Any] | None:
    """Extract thesis from day_story dict and map. None if story missing/unavailable."""
    if not isinstance(story, dict):
        return None
    if str(story.get("interpretation_status") or "").strip() == "unavailable":
        return None
    thesis = story.get("day_thesis") if isinstance(story.get("day_thesis"), dict) else None
    if thesis is None:
        # Fallback: conflict.mode / scenario conflict if nested
        scenario = story.get("day_scenario") if isinstance(story.get("day_scenario"), dict) else {}
        conflict = scenario.get("conflict") if isinstance(scenario.get("conflict"), dict) else {}
        mode = conflict.get("mode") or story.get("mode")
        if mode:
            thesis = {"mode": mode}
    if thesis is None:
        return None
    date_s = local_date
    if not date_s:
        trace = story.get("trace") if isinstance(story.get("trace"), dict) else {}
        date_s = str(trace.get("local_date") or "") or None
    return build_day_atmosphere_v1(day_thesis=thesis, local_date=date_s, hour=hour)
