"""Target architecture: facts / snapshot / job — no LLM on foreign read paths.

Rule: Today / Compatibility / Tarot / account GETs MUST use snapshot or baseline only.
Portrait LLM runs only via ``CoreProfileService.build(..., publish_portrait=True)``
(core-setup, birth-fact save, ``POST /account/core-profile/refresh``).
"""

from __future__ import annotations

from typing import Any, Literal

from todayflow_backend.services.profile_content_v1.source_depth import ProfileSourceDepth

ProfileLayer = Literal["facts", "snapshot", "job"]

# Call sites that previously invoked full build() (LLM-capable) — migrated to cached/baseline.
LLM_ON_READ_RISK_CALLERS: tuple[str, ...] = ()

SAFE_SNAPSHOT_CALLERS: tuple[str, ...] = (
    "GET /account/core-profile",
    "GET /account/profile-summary",
    "GET /account/profile-build-status",
    "GET /account/compact-user-model",
    "POST /today/narrative",
    "POST /tarot/spread/context",
    "questions / day_flow / numerology day context",
    "Today cycle (build_cached_or_baseline)",
    "morning_ritual (build_cached_or_baseline)",
    "compatibility personalized strip (build_cached_or_baseline)",
    "today_story_enrichment_v0 (build_cached_or_baseline)",
)

PORTRAIT_PUBLISHERS: tuple[str, ...] = (
    "POST /account/core-setup",
    "POST/PUT /account/astro-data (save response)",
    "POST /account/core-profile/refresh",
)


def classify_allowed_claims(depth: ProfileSourceDepth) -> dict[str, Any]:
    """What claim classes are allowed at this depth."""
    return {
        "source_depth": depth,
        "general_portrait": True,
        "cite_onboarding_answers": depth
        in ("onboarding_answers", "profile_plus_checkins", "longitudinal_profile"),
        "recurring_patterns": depth in ("profile_plus_checkins", "longitudinal_profile"),
        "longitudinal_claims": depth == "longitudinal_profile",
        "real_stress_behaviour_as_fact": False if depth == "birth_data_only" else "hedged",
    }
