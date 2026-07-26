"""Identity thesis normalization for Stage 2 IDs (not quality scoring).

Maps Stage 1 thesis_key → stable identity_core thesis_key for claim_id fingerprints.
Surface prose comes from the LLM prompt — this module does not judge wording quality.
"""

from __future__ import annotations

# Stage 1 thesis_key → identity-core thesis_key (normalization for stable IDs).
STAGE1_TO_IDENTITY_THESIS: dict[str, str] = {
    "autonomy_high": "builds_through_autonomy",
    "analysis_before_action": "builds_through_analysis",
    "direction_through_air_mind": "builds_through_air_mind",
    "stability_through_earth": "builds_through_earth_stability",
    "care_through_water_sun": "builds_through_water_care",
    "emotional_sensitivity_high": "builds_through_emotional_depth",
    "anchor_through_earth_moon": "builds_through_earth_anchor",
    "freedom_vs_stability": "builds_through_freedom_vs_stability",
    "drive_through_fire_mars": "builds_through_fire_drive",
    "presence_through_air_asc": "builds_through_air_presence",
    "presence_through_fire_asc": "builds_through_fire_presence",
    "presence_through_earth_asc": "builds_through_earth_presence",
    "presence_through_water_asc": "builds_through_water_presence",
}

ALLOWED_IDENTITY_THESIS_KEYS = frozenset(STAGE1_TO_IDENTITY_THESIS.values())

ALLOWED_SOURCE_ROLES = frozenset(
    {
        "dominant_mechanism",
        "supporting_claim",
        "tension_candidate",
        "qualifier",
        "presence_qualifier",
    }
)


def normalize_identity_thesis_key(stage1_thesis_key: str) -> str | None:
    key = (stage1_thesis_key or "").strip()
    return STAGE1_TO_IDENTITY_THESIS.get(key)
