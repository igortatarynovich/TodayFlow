"""Pydantic contracts for base / extended / premium profile content (C3)."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

PROFILE_CONTENT_CONTRACT = "profile_content_v1"
ProfileSourceDepth = Literal[
    "birth_data_only",
    "onboarding_answers",
    "profile_plus_checkins",
    "longitudinal_profile",
]
Confidence = Literal["low", "medium", "high"]
Tier = Literal["base", "extended", "premium"]


def _nonempty(v: str) -> str:
    s = (v or "").strip()
    if not s:
        raise ValueError("empty_field")
    return s


class ProfileBaseContentV1(BaseModel):
    contract_version: str = PROFILE_CONTENT_CONTRACT
    tier: Literal["base"] = "base"
    source_depth: ProfileSourceDepth
    locale: str = "ru"
    headline: str = Field(..., min_length=8, max_length=160)
    core_summary: str = Field(..., min_length=40, max_length=900)
    strengths: list[str] = Field(..., min_length=2, max_length=8)
    emotional_style: str = Field(..., min_length=20, max_length=500)
    communication_style: str = Field(..., min_length=20, max_length=500)
    decision_style: str = Field(..., min_length=20, max_length=500)
    energy_sources: str = Field(..., min_length=15, max_length=420)
    energy_drains: str = Field(..., min_length=15, max_length=420)
    under_pressure: str = Field(..., min_length=20, max_length=500)
    inner_tension: str = Field(..., min_length=20, max_length=500)
    practical_takeaway: str = Field(..., min_length=20, max_length=420)
    confidence: Confidence = "medium"

    @field_validator(
        "headline",
        "core_summary",
        "emotional_style",
        "communication_style",
        "decision_style",
        "energy_sources",
        "energy_drains",
        "under_pressure",
        "inner_tension",
        "practical_takeaway",
    )
    @classmethod
    def _strip(cls, v: str) -> str:
        return _nonempty(v)

    @field_validator("strengths")
    @classmethod
    def _strengths(cls, v: list[str]) -> list[str]:
        out = [str(x).strip() for x in (v or []) if str(x).strip()]
        if len(out) < 2:
            raise ValueError("strengths_too_short")
        return out[:8]


class ProfileExtendedContentV1(ProfileBaseContentV1):
    tier: Literal["extended"] = "extended"  # type: ignore[assignment]
    recurring_patterns: list[str] = Field(default_factory=list)
    avoidance_pattern: str = Field(..., min_length=15, max_length=500)
    recovery_pattern: str = Field(..., min_length=15, max_length=500)
    work_style: str = Field(..., min_length=15, max_length=500)
    relationship_needs: str = Field(..., min_length=15, max_length=500)
    boundaries: str = Field(..., min_length=15, max_length=500)
    current_shift: Optional[str] = Field(None, max_length=500)
    evidence_summary: str = Field(..., min_length=15, max_length=700)


class ProfilePremiumContentV1(BaseModel):
    contract_version: str = PROFILE_CONTENT_CONTRACT
    tier: Literal["premium"] = "premium"
    source_depth: ProfileSourceDepth
    locale: str = "ru"
    direct_answer: Optional[str] = Field(None, max_length=700)
    do: str = Field(..., min_length=15, max_length=420)
    avoid: str = Field(..., min_length=15, max_length=420)
    how: str = Field(..., min_length=15, max_length=500)
    what_to_say: str = Field(..., min_length=15, max_length=420)
    next_step: str = Field(..., min_length=10, max_length=400)
    confidence: Confidence = "medium"

    @field_validator("do", "avoid", "how", "what_to_say", "next_step")
    @classmethod
    def _strip_p(cls, v: str) -> str:
        return _nonempty(v)
