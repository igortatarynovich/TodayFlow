"""Day Atmosphere v1 — closed visual contract for the day.

FOUNDATION_UI §11–§12. Engine output is never colors/CSS — only closed fields.

SoT for visual_mode (2026-08-10):
  1. LLM-chosen mood from the closed 8-set (day story / native scenario), if valid
  2. Else deterministic thesis.mode → visual_mode map (fallback)

Intensity / warmth / contrast follow the resolved visual_mode so shell stays coherent.
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

# Product mood labels (RU) — same closed set as FE DAY_MODE_LABELS_RU
VISUAL_MODE_LABELS_RU: dict[str, str] = {
    "grounded": "Заземление",
    "flow": "Поток",
    "radiance": "Сияние",
    "momentum": "Импульс",
    "clarity": "Ясность",
    "tension": "Напряжение",
    "renewal": "Обновление",
    "depth": "Глубина",
}

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

# thesis.mode → base visual_mode (before night/depth soft path) — fallback only
_MODE_TO_VISUAL: dict[str, str] = {
    "stability": "grounded",
    "recovery": "renewal",
    "opportunity": "radiance",
    "transition": "flow",
    "conflict": "tension",
    "pressure": "tension",
    "change": "momentum",
}

# Defaults keyed by resolved visual_mode (LLM pick or thesis fallback)
_VISUAL_INTENSITY: dict[str, float] = {
    "grounded": 0.32,
    "flow": 0.48,
    "radiance": 0.52,
    "momentum": 0.66,
    "clarity": 0.4,
    "tension": 0.72,
    "renewal": 0.36,
    "depth": 0.3,
}

_VISUAL_CONTRAST: dict[str, str] = {
    "grounded": "soft",
    "flow": "medium",
    "radiance": "medium",
    "momentum": "strong",
    "clarity": "medium",
    "tension": "strong",
    "renewal": "soft",
    "depth": "soft",
}

_VISUAL_WARMTH: dict[str, float] = {
    "grounded": 0.62,
    "flow": 0.45,
    "radiance": 0.7,
    "momentum": 0.55,
    "clarity": 0.4,
    "tension": 0.35,
    "renewal": 0.55,
    "depth": 0.35,
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


def normalize_visual_mode(value: Any) -> str | None:
    """Return closed visual_mode id or None if missing/invalid."""
    if value is None:
        return None
    mode = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    # Accept accidental RU labels via reverse map
    if mode not in VISUAL_MODES:
        for vid, label in VISUAL_MODE_LABELS_RU.items():
            if mode == label.lower():
                return vid
        return None
    return mode


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
    """Closed mapping — never returns an open string. Fallback when LLM mood absent."""
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
    visual_mode: str | None = None,
) -> dict[str, Any]:
    """Build public nest for today_contract. Always returns a full closed dict.

    ``visual_mode`` — optional LLM/story hint; invalid/missing → thesis map fallback.
    """
    thesis = day_thesis if isinstance(day_thesis, dict) else {}
    thesis_mode = str(thesis.get("mode") or "").strip().lower() or "stability"

    phase = (time_phase or "").strip().lower()
    if phase not in ("morning", "day", "evening", "night"):
        phase = time_phase_from_hour(hour if hour is not None else datetime.now().hour)

    llm_mode = normalize_visual_mode(visual_mode)
    resolved = llm_mode or map_thesis_mode_to_visual(thesis_mode, time_phase=phase)

    intensity = float(_VISUAL_INTENSITY.get(resolved, 0.4))
    warmth = float(_VISUAL_WARMTH.get(resolved, 0.5))
    contrast = _VISUAL_CONTRAST.get(resolved, "medium")
    motion = "none" if resolved in ("depth", "grounded") and intensity < 0.4 else "low"
    decor = _pick_decor(resolved, local_date=local_date, thesis_mode=thesis_mode)

    return {
        "version": DAY_ATMOSPHERE_VERSION,
        "visual_mode": resolved,
        "intensity": intensity,
        "warmth": warmth,
        "motion": motion,
        "contrast": contrast,
        "decor_variant": decor,
        "time_phase": phase,
    }


def _visual_mode_from_story(story: dict[str, Any]) -> str | None:
    """Prefer story-level LLM mood, then nested scenario."""
    direct = normalize_visual_mode(story.get("visual_mode"))
    if direct:
        return direct
    atm = story.get("day_atmosphere") if isinstance(story.get("day_atmosphere"), dict) else {}
    nested_atm = normalize_visual_mode(atm.get("visual_mode"))
    if nested_atm:
        return nested_atm
    scen = story.get("day_scenario") if isinstance(story.get("day_scenario"), dict) else {}
    return normalize_visual_mode(scen.get("visual_mode"))


def day_atmosphere_from_story(
    story: dict[str, Any] | None,
    *,
    local_date: str | None = None,
    hour: int | None = None,
) -> dict[str, Any] | None:
    """Extract thesis (+ optional LLM visual_mode) from day_story. None if unavailable."""
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
        if not mode:
            c_thesis = conflict.get("thesis") if isinstance(conflict.get("thesis"), dict) else {}
            mode = c_thesis.get("mode")
        if mode:
            thesis = {"mode": mode}
    if thesis is None:
        return None
    date_s = local_date
    if not date_s:
        trace = story.get("trace") if isinstance(story.get("trace"), dict) else {}
        date_s = str(trace.get("local_date") or "") or None
    return build_day_atmosphere_v1(
        day_thesis=thesis,
        local_date=date_s,
        hour=hour,
        visual_mode=_visual_mode_from_story(story),
    )
