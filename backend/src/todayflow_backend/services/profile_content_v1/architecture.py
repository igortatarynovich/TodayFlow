"""Target architecture: facts / snapshot / job — no LLM on foreign read paths.

Current risk (C3 audit): CoreProfileService.build() still runs the portrait
funnel synchronously on GET /account/core-profile and several side modules.

Target:
  profile_facts       — deterministic inputs (birth, numbers, onboarding answers)
  profile_snapshot    — last validated interpretation (ready/partial)
  profile_generation_job — background enrichment (reuse generation_jobs_v0)
  profile_version / profile_fingerprint — cache keys

Rule: Today / Compatibility / Tarot MUST use snapshot or baseline only.
"""

from __future__ import annotations

from typing import Any, Literal

from todayflow_backend.services.profile_content_v1.source_depth import ProfileSourceDepth

ProfileLayer = Literal["facts", "snapshot", "job"]

# Known call sites that still invoke full build() (LLM-capable) — migrate off.
LLM_ON_READ_RISK_CALLERS: tuple[str, ...] = (
    "GET /account/core-profile",
    "GET /account/profile-summary",
    "GET /account/profile-build-status",
    "GET /account/compact-user-model",
    "POST /today/narrative",
    "POST /tarot/spread/context",
    "questions / day_flow / numerology day context",
)

SAFE_SNAPSHOT_CALLERS: tuple[str, ...] = (
    "Today cycle (build_cached_or_baseline)",
    "morning_ritual (build_cached_or_baseline)",
    "compatibility personalized strip (build_cached_or_baseline)",
    "today_story_enrichment_v0 (build_cached_or_baseline)",
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
