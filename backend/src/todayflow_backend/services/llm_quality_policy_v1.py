"""LLM quality policy v1 — quality-first vs legacy economize.

Canon shift (2026-07): platform no longer optimizes for token scarcity by default.
``LLM_QUALITY_MODE=rich`` (default): generous max_tokens, standard model tier for all
Today surfaces, full context depth, larger prompt packs, multi-step funnels preferred.

``economize`` keeps the previous AMLL cost-control tables for constrained environments.
"""

from __future__ import annotations

from typing import Any, Literal

from todayflow_backend.core.config import settings

LLM_QUALITY_POLICY_V1 = "llm_quality_policy_v1"

QualityMode = Literal["rich", "economize"]

# Rich budgets: enough for substantive JSON + reasoning headroom on open models.
RICH_MAX_TOKENS_BY_SURFACE: dict[str, dict[str, int]] = {
    "guide": {"quick": 2200, "normal": 4096, "deep": 6144},
    "day_layer": {"quick": 1800, "normal": 3200, "deep": 4800},
    "spheres": {"quick": 1400, "normal": 2800, "deep": 4000},
    "evening": {"quick": 1200, "normal": 2400, "deep": 3600},
    "deepen": {"quick": 1600, "normal": 3200, "deep": 4800},
}

ECONOMIZE_MAX_TOKENS_BY_SURFACE: dict[str, dict[str, int]] = {
    "guide": {"quick": 950, "normal": 1750, "deep": 2100},
    "day_layer": {"quick": 700, "normal": 1200, "deep": 1500},
    "spheres": {"quick": 500, "normal": 800, "deep": 1000},
    "evening": {"quick": 500, "normal": 800, "deep": 1000},
    "deepen": {"quick": 600, "normal": 1000, "deep": 1300},
}

# Per-step funnel budgets (guide + child disclosure funnels + profile).
RICH_FUNNEL_STEP_TOKENS: dict[str, int] = {
    "quick": 1800,
    "normal": 3200,
    "deep": 4800,
}

ECONOMIZE_FUNNEL_STEP_TOKENS: dict[str, int] = {
    "quick": 720,
    "normal": 1200,
    "deep": 1600,
}

# User JSON pack char budgets (prompt context, not completion).
RICH_USER_JSON_CHARS = 48000
ECONOMIZE_USER_JSON_CHARS = 12000

RICH_PROFILE_SLICE_CLIP = {
    "display_name": 120,
    "sun_sign": 80,
    "intention": 800,
    "morning_focus": 200,
    "head_topic": 240,
    "mood": 120,
    "learning_summary": 1200,
    "pattern_hint": 400,
    "weak_or_best": 280,
    "goal_title": 200,
}

ECONOMIZE_PROFILE_SLICE_CLIP = {
    "display_name": 80,
    "sun_sign": 48,
    "intention": 400,
    "morning_focus": 100,
    "head_topic": 120,
    "mood": 80,
    "learning_summary": 480,
    "pattern_hint": 220,
    "weak_or_best": 160,
    "goal_title": 120,
}


def normalize_quality_mode(raw: str | None = None) -> QualityMode:
    mode = (raw if raw is not None else settings.llm_quality_mode or "rich").strip().lower()
    return "economize" if mode == "economize" else "rich"


def is_rich_quality_mode(raw: str | None = None) -> bool:
    return normalize_quality_mode(raw) == "rich"


def max_tokens_for_surface(surface: str, depth_level: str, *, mode: str | None = None) -> int:
    qm = normalize_quality_mode(mode)
    depth = depth_level if depth_level in ("quick", "normal", "deep") else "normal"
    table = RICH_MAX_TOKENS_BY_SURFACE if qm == "rich" else ECONOMIZE_MAX_TOKENS_BY_SURFACE
    row = table.get(surface) or table["guide"]
    return int(row.get(depth) or row["normal"])


def funnel_step_max_tokens(depth_level: str, *, mode: str | None = None) -> int:
    qm = normalize_quality_mode(mode)
    depth = depth_level if depth_level in ("quick", "normal", "deep") else "normal"
    table = RICH_FUNNEL_STEP_TOKENS if qm == "rich" else ECONOMIZE_FUNNEL_STEP_TOKENS
    return int(table.get(depth) or table["normal"])


def user_json_char_budget(*, mode: str | None = None) -> int:
    return RICH_USER_JSON_CHARS if is_rich_quality_mode(mode) else ECONOMIZE_USER_JSON_CHARS


def profile_slice_clips(*, mode: str | None = None) -> dict[str, int]:
    return dict(RICH_PROFILE_SLICE_CLIP if is_rich_quality_mode(mode) else ECONOMIZE_PROFILE_SLICE_CLIP)


def model_tier_for_surface(surface: str, depth_level: str, *, mode: str | None = None) -> str:
    """In rich mode every narrative surface uses the standard tier."""
    if is_rich_quality_mode(mode):
        return "standard"
    if surface in ("spheres", "evening"):
        return "cheap"
    if surface == "deepen" and depth_level == "quick":
        return "cheap"
    return "standard"


def context_depth_for_surface(
    surface: str,
    user_context: dict[str, Any],
    *,
    mode: str | None = None,
) -> str:
    if is_rich_quality_mode(mode):
        if user_context.get("has_day_context"):
            return "standard"
        return "minimal"
    if not user_context.get("has_day_context"):
        return "minimal"
    if surface == "guide":
        return "standard"
    if int(user_context.get("behavior_event_count") or 0) >= 3:
        return "standard"
    return "minimal"


def prefer_multi_step_funnels(*, mode: str | None = None) -> bool:
    """Rich mode always prefers disclosure funnels over one-shot monoliths."""
    return is_rich_quality_mode(mode)


def quality_policy_snapshot(*, mode: str | None = None) -> dict[str, Any]:
    qm = normalize_quality_mode(mode)
    return {
        "contract_version": LLM_QUALITY_POLICY_V1,
        "mode": qm,
        "prefer_multi_step_funnels": prefer_multi_step_funnels(mode=qm),
        "user_json_char_budget": user_json_char_budget(mode=qm),
        "provider": (settings.llm_provider or "openai").strip().lower(),
    }
