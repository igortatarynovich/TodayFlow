"""Pydantic contracts for Guest / Registered / Premium content layers."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

CONTENT_CONTRACT_VERSION = "compatibility_content_v1"

SourceDepth = Literal["zodiac_only", "birth_dates", "profile_enriched", "two_profiles"]
Confidence = Literal["low", "medium", "high"]
Verdict = Literal["да", "скорее да", "зависит", "скорее нет", "нет"]
Tier = Literal["guest", "registered", "premium"]


def _nonempty(v: str) -> str:
    s = (v or "").strip()
    if not s:
        raise ValueError("empty_field")
    return s


class ContentBaseV1(BaseModel):
    contract_version: str = CONTENT_CONTRACT_VERSION
    tier: Tier
    source_depth: SourceDepth
    locale: str = "ru"
    headline: str = Field(..., min_length=8, max_length=160)
    score: int = Field(..., ge=0, le=100)
    summary: str = Field(..., min_length=40, max_length=900)
    attraction: str = Field(..., min_length=20, max_length=420)
    main_risk: str = Field(..., min_length=20, max_length=420)
    practical_advice: str = Field(..., min_length=20, max_length=420)
    confidence: Confidence = "medium"

    @field_validator("headline", "summary", "attraction", "main_risk", "practical_advice")
    @classmethod
    def _strip_required(cls, v: str) -> str:
        return _nonempty(v)


class GuestContentV1(ContentBaseV1):
    """Finished guest teaser — not a truncated registered surface."""

    tier: Literal["guest"] = "guest"
    locked_preview: list[str] = Field(default_factory=list, min_length=2, max_length=6)

    @field_validator("locked_preview")
    @classmethod
    def _preview_items(cls, v: list[str]) -> list[str]:
        out = [str(x).strip() for x in (v or []) if str(x).strip()]
        if len(out) < 2:
            raise ValueError("locked_preview_too_short")
        return out[:6]


class RegisteredContentV1(ContentBaseV1):
    """Deep relationship reading — each block answers a distinct question."""

    tier: Literal["registered"] = "registered"
    emotions: str = Field(..., min_length=40, max_length=700)
    communication: str = Field(..., min_length=40, max_length=700)
    conflict: str = Field(..., min_length=40, max_length=700)
    strengths: str = Field(..., min_length=40, max_length=700)
    vulnerable_spot: str = Field(..., min_length=30, max_length=500)
    what_helps: str = Field(..., min_length=30, max_length=500)

    @field_validator(
        "emotions",
        "communication",
        "conflict",
        "strengths",
        "vulnerable_spot",
        "what_helps",
    )
    @classmethod
    def _strip_blocks(cls, v: str) -> str:
        return _nonempty(v)


class PremiumContentV1(BaseModel):
    """Decision tool — useful, not merely longer."""

    contract_version: str = CONTENT_CONTRACT_VERSION
    tier: Literal["premium"] = "premium"
    source_depth: SourceDepth
    locale: str = "ru"
    verdict: Verdict
    verdict_reason: str = Field(..., min_length=30, max_length=500)
    do: str = Field(..., min_length=20, max_length=420)
    avoid: str = Field(..., min_length=20, max_length=420)
    how: str = Field(..., min_length=20, max_length=500)
    what_to_say: str = Field(..., min_length=20, max_length=420)
    focus_now: str = Field(..., min_length=20, max_length=420)
    next_step: str = Field(..., min_length=15, max_length=320)
    direct_answer: Optional[str] = Field(None, max_length=700)
    confidence: Confidence = "medium"
    score: Optional[int] = Field(None, ge=0, le=100)

    @field_validator(
        "verdict_reason",
        "do",
        "avoid",
        "how",
        "what_to_say",
        "focus_now",
        "next_step",
    )
    @classmethod
    def _strip_premium(cls, v: str) -> str:
        return _nonempty(v)
