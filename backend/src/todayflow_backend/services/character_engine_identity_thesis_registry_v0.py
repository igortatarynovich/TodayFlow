"""Identity thesis normalization for Stage 2 IDs (not quality scoring).

Maps Stage 1 thesis_key → stable identity_core thesis_key for claim_id fingerprints.
Surface prose comes from the LLM prompt — this module does not judge wording quality.
"""

from __future__ import annotations

# Stage 1 thesis_key → identity-core thesis_key (normalization for stable IDs).
STAGE1_TO_IDENTITY_THESIS: dict[str, str] = {
    "autonomy_high": "builds_through_autonomy",
    "analysis_before_action": "builds_through_analysis",
    "emotional_sensitivity_high": "builds_through_emotional_depth",
    "freedom_vs_stability": "builds_through_freedom_vs_stability",
    "presence_through_air_asc": "builds_through_air_presence",
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
