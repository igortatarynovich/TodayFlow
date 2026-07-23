"""Shared types for Canonical Context Engine v0."""

from __future__ import annotations

from typing import Any, Literal, TypedDict

CONTEXT_ENGINE_VERSION = "context_engine_v0.1"
CONTEXT_PACK_CONTRACT = "context_pack_v0"

Confidence = Literal["high", "medium", "low", "unknown"]


class FactAtom(TypedDict, total=False):
    id: str
    domain: str
    source: str
    value: Any
    confidence: Confidence
    eligibility: bool
    dependencies: list[str]
    calculation_version: str | None
    limitations: list[str]


class Cue(TypedDict, total=False):
    id: str
    text: str
    fact_ids: list[str]


class QuestionSpec(TypedDict, total=False):
    question_id: str
    domain: str
    """Legacy Profile chrome id when this question backs a sphere card."""
    sphere_id: str | None
    user_question: str
    user_value: str
    prompt_id: str
    style_fact_id: str
    style_key: str
    natal_planets: list[str]
    house_numbers: list[str]
    living_fact_ids: list[str]
    patterns_fact_ids: list[str]


class ContextPack(TypedDict, total=False):
    contract_version: str
    question_id: str
    domain: str
    sphere_id: str | None
    locale: str
    user_question: str
    user_value: str
    identity_core: str
    strengths: list[Any]
    growth_zones: list[Any]
    relevant_style: str
    cues: list[Cue]
    house_cues: list[Cue]
    fact_ids: list[str]
    omitted_facts: list[dict[str, str]]
    context_version: str
    fingerprint: str
    kitchen: dict[str, Any]
