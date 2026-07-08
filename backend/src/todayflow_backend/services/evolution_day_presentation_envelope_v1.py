"""B1.10 — Evolution Day Presentation Envelope (B1.7 day_engine slice)."""

from __future__ import annotations

import copy
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.day_model_v1_day_engine_knowledge_wiring import (
    GUIDE_DECISION_CONTRACT,
    extract_day_model_core_snapshot,
)
from todayflow_backend.services.day_model_v1_hint_application import compute_state_snapshot_hash
from todayflow_backend.services.evolution_effect_consumer_map_v1 import (
    CONSUMER_DAY_ENGINE,
    EVOLUTION_EFFECT_CONSUMER_SLICE_V1_CONTRACT,
    validate_evolution_effect_consumer_slice_v1,
)
from todayflow_backend.services.evolution_effect_runtime_policy_v1 import (
    EVOLUTION_EFFECT_RUNTIME_POLICY_V1_CONTRACT,
)

EVOLUTION_DAY_PRESENTATION_ENVELOPE_V1_VERSION = "1.0.0"

EVOLUTION_DAY_PRESENTATION_ENVELOPE_V1_CONTRACT = "evolution_day_presentation_envelope_v1"

ANSWER_DEPTH_MINIMAL = "minimal"
ANSWER_DEPTH_NORMAL = "normal"
ANSWER_DEPTH_DEEP = "deep"

TONE_SIMPLE = "simple"
TONE_NEUTRAL = "neutral"
TONE_REFLECTIVE = "reflective"
TONE_STRATEGIC = "strategic"

DEPTH_ORDER = {
    ANSWER_DEPTH_MINIMAL: 0,
    ANSWER_DEPTH_NORMAL: 1,
    ANSWER_DEPTH_DEEP: 2,
}

STAGE_PRESENTATION_PROFILES: dict[str, dict[str, Any]] = {
    "seeker": {
        "tone_policy": TONE_SIMPLE,
        "answer_depth_cap": ANSWER_DEPTH_MINIMAL,
        "interpretation_cap": 1,
        "surface_priority_hints": ["today_hero", "tempo_card"],
    },
    "observer": {
        "tone_policy": TONE_REFLECTIVE,
        "answer_depth_cap": ANSWER_DEPTH_MINIMAL,
        "interpretation_cap": 2,
        "surface_priority_hints": ["reflection_card", "day_guidance_card"],
    },
    "practitioner": {
        "tone_policy": TONE_NEUTRAL,
        "answer_depth_cap": ANSWER_DEPTH_NORMAL,
        "interpretation_cap": 3,
        "surface_priority_hints": ["action_card", "day_guidance_card"],
    },
    "explorer": {
        "tone_policy": TONE_NEUTRAL,
        "answer_depth_cap": ANSWER_DEPTH_NORMAL,
        "interpretation_cap": 3,
        "surface_priority_hints": ["day_guidance_card", "reflection_card"],
    },
    "architect": {
        "tone_policy": TONE_STRATEGIC,
        "answer_depth_cap": ANSWER_DEPTH_DEEP,
        "interpretation_cap": 4,
        "surface_priority_hints": ["day_guidance_card", "action_card", "reflection_card"],
    },
    "mentor": {
        "tone_policy": TONE_REFLECTIVE,
        "answer_depth_cap": ANSWER_DEPTH_DEEP,
        "interpretation_cap": 5,
        "surface_priority_hints": ["reflection_card", "day_guidance_card"],
    },
    "master": {
        "tone_policy": TONE_STRATEGIC,
        "answer_depth_cap": ANSWER_DEPTH_DEEP,
        "interpretation_cap": 5,
        "surface_priority_hints": ["today_hero", "day_guidance_card"],
    },
}

BUDGET_DEPTH_CAP = {
    "none": ANSWER_DEPTH_MINIMAL,
    "low": ANSWER_DEPTH_MINIMAL,
    "medium": ANSWER_DEPTH_NORMAL,
    "high": ANSWER_DEPTH_DEEP,
}

EVOLUTION_DAY_PRESENTATION_ENVELOPE_V1_KEYS = frozenset(
    {
        "contract_version",
        "envelope_id",
        "source_day_model_hash",
        "source_evolution_slice_id",
        "evolution_stage",
        "answer_depth_cap",
        "tone_policy",
        "interpretation_cap",
        "surface_priority_hints",
        "knowledge_coexistence_trace",
        "blocked_effects",
        "core_daymodel_mutated",
        "created_at",
    }
)

FORBIDDEN_ENVELOPE_MUTATION_FIELDS = frozenset(
    {
        "vector",
        "strategy",
        "risk",
        "tempo",
        "source_weights",
        "recommendation",
        "commerce",
        "stage_update",
        "llm_call",
    }
)

GUIDE_DECISION_SEMANTIC_KEYS = frozenset(
    {
        "contract_version",
        "locale",
        "headline",
        "subline",
        "core_message",
        "do_items",
        "avoid_items",
        "energy_line",
        "focus_line",
        "risk_line",
        "risk_detail",
        "anchors",
        "knowledge_hints",
    }
)


class EvolutionDayPresentationEnvelopeError(ValueError):
    """Raised when presentation envelope inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_envelope_id() -> str:
    return f"edpe-{uuid4()}"


def _day_model_hash(day_model: dict[str, Any] | None) -> str | None:
    if not isinstance(day_model, dict):
        return None
    return compute_state_snapshot_hash(extract_day_model_core_snapshot(day_model))


def _knowledge_coexistence_trace(
    knowledge_input: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not isinstance(knowledge_input, dict):
        return None
    return {
        "integration_id": knowledge_input.get("integration_id"),
        "context_slice_id": knowledge_input.get("context_slice_id"),
        "contract_version": knowledge_input.get("contract_version"),
    }


def _idle_envelope(
    *,
    blocked_effects: list[str],
    source_day_model_hash: str | None = None,
    knowledge_coexistence_trace: dict[str, Any] | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    return {
        "contract_version": EVOLUTION_DAY_PRESENTATION_ENVELOPE_V1_CONTRACT,
        "envelope_id": generate_envelope_id(),
        "source_day_model_hash": source_day_model_hash,
        "source_evolution_slice_id": None,
        "evolution_stage": None,
        "answer_depth_cap": None,
        "tone_policy": None,
        "interpretation_cap": None,
        "surface_priority_hints": [],
        "knowledge_coexistence_trace": knowledge_coexistence_trace,
        "blocked_effects": blocked_effects,
        "core_daymodel_mutated": False,
        "created_at": created_at or _utc_now_iso(),
    }


def _min_depth(current: str, cap: str) -> str:
    if DEPTH_ORDER.get(current, 0) <= DEPTH_ORDER.get(cap, 0):
        return current
    return cap


def _is_valid_day_engine_slice(evolution_slice: dict[str, Any]) -> tuple[bool, str | None]:
    if evolution_slice.get("contract_version") == EVOLUTION_EFFECT_RUNTIME_POLICY_V1_CONTRACT:
        return False, "full_policy_not_accepted"
    if evolution_slice.get("contract_version") != EVOLUTION_EFFECT_CONSUMER_SLICE_V1_CONTRACT:
        return False, "invalid_slice_contract"
    if evolution_slice.get("consumer_id") != CONSUMER_DAY_ENGINE:
        return False, "invalid_consumer_id"
    errors = validate_evolution_effect_consumer_slice_v1(
        evolution_slice,
        consumer_id=CONSUMER_DAY_ENGINE,
    )
    if errors:
        return False, "invalid_slice_payload"
    return True, None


def extract_guide_decision_semantic_snapshot(guide_decision: dict[str, Any]) -> dict[str, Any]:
    """Semantic guide_decision fields the presentation envelope must not mutate."""
    return {key: copy.deepcopy(guide_decision.get(key)) for key in GUIDE_DECISION_SEMANTIC_KEYS}


def build_evolution_day_presentation_envelope_v1(
    evolution_slice: dict[str, Any],
    *,
    day_model: dict[str, Any] | None = None,
    knowledge_input: dict[str, Any] | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build presentation envelope from a validated B1.7 day_engine slice."""
    valid, reason = _is_valid_day_engine_slice(evolution_slice)
    if not valid:
        raise EvolutionDayPresentationEnvelopeError(reason or "invalid evolution slice")

    stage = str(evolution_slice.get("current_stage") or "seeker")
    profile = STAGE_PRESENTATION_PROFILES.get(stage, STAGE_PRESENTATION_PROFILES["seeker"])

    limits = evolution_slice.get("effect_limits") or {}
    engine = (evolution_slice.get("allowed_effects") or {}).get("engine_effects") or {}

    max_context_lines = limits.get("max_context_lines")
    if max_context_lines is None:
        max_context_lines = engine.get("max_context_lines", 0)
    llm_budget_tier = limits.get("llm_budget_tier") or engine.get("llm_budget_tier") or "none"

    blocked_effects: list[str] = []
    line_cap = max(0, int(max_context_lines))

    answer_depth_cap = profile["answer_depth_cap"]
    budget_depth_cap = BUDGET_DEPTH_CAP.get(str(llm_budget_tier), ANSWER_DEPTH_MINIMAL)
    if DEPTH_ORDER.get(answer_depth_cap, 0) > DEPTH_ORDER.get(budget_depth_cap, 0):
        blocked_effects.append(f"answer_depth:{answer_depth_cap}->{budget_depth_cap}")
        answer_depth_cap = budget_depth_cap

    if line_cap <= 0:
        if answer_depth_cap != ANSWER_DEPTH_MINIMAL:
            blocked_effects.append(f"answer_depth:{answer_depth_cap}->{ANSWER_DEPTH_MINIMAL}")
        answer_depth_cap = ANSWER_DEPTH_MINIMAL
    elif line_cap <= 2:
        capped = _min_depth(answer_depth_cap, ANSWER_DEPTH_NORMAL)
        if capped != answer_depth_cap:
            blocked_effects.append(f"answer_depth:{answer_depth_cap}->{capped}")
        answer_depth_cap = capped

    interpretation_cap = int(profile["interpretation_cap"])
    if interpretation_cap > line_cap:
        blocked_effects.append(f"interpretation_cap:{interpretation_cap}->{line_cap}")
        interpretation_cap = line_cap

    return {
        "contract_version": EVOLUTION_DAY_PRESENTATION_ENVELOPE_V1_CONTRACT,
        "envelope_id": generate_envelope_id(),
        "source_day_model_hash": _day_model_hash(day_model),
        "source_evolution_slice_id": evolution_slice.get("slice_id"),
        "evolution_stage": stage,
        "answer_depth_cap": answer_depth_cap,
        "tone_policy": profile["tone_policy"],
        "interpretation_cap": interpretation_cap,
        "surface_priority_hints": list(profile["surface_priority_hints"]),
        "knowledge_coexistence_trace": _knowledge_coexistence_trace(knowledge_input),
        "blocked_effects": blocked_effects,
        "core_daymodel_mutated": False,
        "created_at": created_at or _utc_now_iso(),
    }


def attach_evolution_day_presentation_envelope_v1(
    guide_decision: dict[str, Any],
    evolution_slice: dict[str, Any] | None = None,
    *,
    day_model: dict[str, Any] | None = None,
    knowledge_input: dict[str, Any] | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """
    Attach read-only evolution presentation envelope to guide_decision.

    Day Engine result + envelope = stage-aware presentation constraints.
    Does not mutate DayModel or guide_decision semantic fields.
    """
    if guide_decision.get("contract_version") != GUIDE_DECISION_CONTRACT:
        raise EvolutionDayPresentationEnvelopeError("invalid guide_decision contract_version")

    day_model_before = (
        extract_day_model_core_snapshot(day_model) if isinstance(day_model, dict) else None
    )

    wired = copy.deepcopy(guide_decision)
    wired.pop("evolution_day_presentation_envelope", None)
    wired.pop("evolution_presentation_envelope", None)

    semantic_before = extract_guide_decision_semantic_snapshot(guide_decision)
    model_hash = _day_model_hash(day_model)
    knowledge_trace = _knowledge_coexistence_trace(knowledge_input)

    if evolution_slice is None:
        envelope = _idle_envelope(
            blocked_effects=["ignored:no_evolution_slice"],
            source_day_model_hash=model_hash,
            knowledge_coexistence_trace=knowledge_trace,
            created_at=created_at,
        )
    else:
        valid, invalid_reason = _is_valid_day_engine_slice(evolution_slice)
        if not valid:
            envelope = _idle_envelope(
                blocked_effects=[f"ignored:{invalid_reason}"],
                source_day_model_hash=model_hash,
                knowledge_coexistence_trace=knowledge_trace,
                created_at=created_at,
            )
        else:
            envelope = build_evolution_day_presentation_envelope_v1(
                evolution_slice,
                day_model=day_model,
                knowledge_input=knowledge_input,
                created_at=created_at,
            )

    envelope_errors = validate_evolution_day_presentation_envelope_v1(envelope)
    if envelope_errors:
        raise EvolutionDayPresentationEnvelopeError("; ".join(envelope_errors))

    semantic_after = extract_guide_decision_semantic_snapshot(wired)
    if semantic_before != semantic_after:
        raise EvolutionDayPresentationEnvelopeError("guide_decision semantic fields mutated")

    day_model_mutated = False
    if day_model_before is not None and isinstance(day_model, dict):
        day_model_mutated = extract_day_model_core_snapshot(day_model) != day_model_before

    envelope["core_daymodel_mutated"] = day_model_mutated
    wired["evolution_day_presentation_envelope"] = envelope
    return wired


def wire_guide_decision_with_evolution_presentation_v1(
    guide_decision: dict[str, Any],
    *,
    evolution_slice: dict[str, Any] | None = None,
    day_model: dict[str, Any] | None = None,
    knowledge_input: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Guide decision + optional B1.10 evolution day presentation envelope."""
    return attach_evolution_day_presentation_envelope_v1(
        guide_decision,
        evolution_slice,
        day_model=day_model,
        knowledge_input=knowledge_input,
    )


def validate_evolution_day_presentation_envelope_v1(envelope: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if envelope.get("contract_version") != EVOLUTION_DAY_PRESENTATION_ENVELOPE_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in EVOLUTION_DAY_PRESENTATION_ENVELOPE_V1_KEYS:
        if key not in envelope:
            errors.append(f"missing envelope field: {key}")

    forbidden = set(envelope.keys()) & FORBIDDEN_ENVELOPE_MUTATION_FIELDS
    if forbidden:
        errors.append(f"forbidden envelope mutation fields: {sorted(forbidden)}")

    if not isinstance(envelope.get("surface_priority_hints"), list):
        errors.append("surface_priority_hints must be array")
    if not isinstance(envelope.get("blocked_effects"), list):
        errors.append("blocked_effects must be array")

    if envelope.get("core_daymodel_mutated") is not False:
        errors.append("core_daymodel_mutated must be false")

    if envelope.get("source_evolution_slice_id") is not None:
        if envelope.get("evolution_stage") is None:
            errors.append("evolution_stage required when slice attached")
        if envelope.get("answer_depth_cap") is None:
            errors.append("answer_depth_cap required when slice attached")
        if envelope.get("tone_policy") is None:
            errors.append("tone_policy required when slice attached")
        if envelope.get("interpretation_cap") is None:
            errors.append("interpretation_cap required when slice attached")

    extra = set(envelope.keys()) - EVOLUTION_DAY_PRESENTATION_ENVELOPE_V1_KEYS
    if extra:
        errors.append(f"unexpected envelope fields: {sorted(extra)}")

    return errors


def validate_guide_decision_with_evolution_presentation_envelope_v1(
    guide_decision: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    if guide_decision.get("contract_version") != GUIDE_DECISION_CONTRACT:
        errors.append("invalid guide_decision contract_version")

    envelope = guide_decision.get("evolution_day_presentation_envelope")
    if envelope is None:
        errors.append("missing evolution_day_presentation_envelope")
        return errors

    errors.extend(validate_evolution_day_presentation_envelope_v1(envelope))

    forbidden = set(guide_decision.keys()) & {
        "blocked_effects",
        "stage_effects_ref",
        "evolution_score_snapshot_id",
        "allowed_effects",
        "effect_limits",
    }
    if forbidden:
        errors.append(f"forbidden evolution policy fields on guide_decision: {sorted(forbidden)}")

    return errors
