"""B1.11 — Evolution → Practice Selector filter (B1.7 practice_selector slice as cap layer)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.evolution_effect_consumer_map_v1 import (
    CONSUMER_PRACTICE_SELECTOR,
    EVOLUTION_EFFECT_CONSUMER_SLICE_V1_CONTRACT,
    validate_evolution_effect_consumer_slice_v1,
)
from todayflow_backend.services.evolution_effect_runtime_policy_v1 import (
    EVOLUTION_EFFECT_RUNTIME_POLICY_V1_CONTRACT,
)

EVOLUTION_PRACTICE_SELECTOR_FILTER_V1_VERSION = "1.0.0"

EVOLUTION_PRACTICE_SELECTOR_FILTER_V1_CONTRACT = "evolution_practice_selector_filter_v1"

COMPLEXITY_BEGINNER = "beginner"
COMPLEXITY_INTERMEDIATE = "intermediate"
COMPLEXITY_ADVANCED = "advanced"

ENTITY_TYPE_PRACTICE = "practice"
ENTITY_TYPE_HABIT = "habit"
ENTITY_TYPE_RITUAL = "ritual"
ENTITY_TYPE_CYCLE = "cycle"

ALLOWED_ENTITY_TYPES = frozenset(
    {ENTITY_TYPE_PRACTICE, ENTITY_TYPE_HABIT, ENTITY_TYPE_RITUAL, ENTITY_TYPE_CYCLE}
)

COMPLEXITY_ORDER = {
    COMPLEXITY_BEGINNER: 0,
    COMPLEXITY_INTERMEDIATE: 1,
    COMPLEXITY_ADVANCED: 2,
}

PACK_TIER_ORDER = {
    "starter": 0,
    "core": 1,
    "advanced": 2,
    "full": 3,
}

PACK_TIER_MAX_COMPLEXITY = {
    "starter": COMPLEXITY_BEGINNER,
    "core": COMPLEXITY_INTERMEDIATE,
    "advanced": COMPLEXITY_ADVANCED,
    "full": COMPLEXITY_ADVANCED,
}

BLOCK_COMPLEXITY_ABOVE_STAGE = "complexity_above_stage"
BLOCK_PATH_THEME_NOT_ALLOWED = "path_theme_not_allowed"
BLOCK_DURATION_ABOVE_CAP = "duration_above_cap"
BLOCK_ENTITY_TYPE_NOT_ALLOWED = "entity_type_not_allowed"
BLOCK_SAFETY_NOTE_REQUIRED = "safety_note_required"
BLOCK_MISSING_DEFINITION = "missing_definition"
BLOCK_INVALID_EVOLUTION_SLICE = "invalid_evolution_slice"

STAGE_PRACTICE_LIMITS: dict[str, dict[str, Any]] = {
    "seeker": {
        "allowed_complexity_levels": {COMPLEXITY_BEGINNER},
        "allowed_entity_types": {ENTITY_TYPE_PRACTICE},
        "max_duration_minutes": 10,
        "safety_gated": False,
    },
    "observer": {
        "allowed_complexity_levels": {COMPLEXITY_BEGINNER},
        "allowed_entity_types": {ENTITY_TYPE_PRACTICE, ENTITY_TYPE_HABIT},
        "max_duration_minutes": 15,
        "safety_gated": False,
    },
    "practitioner": {
        "allowed_complexity_levels": {COMPLEXITY_BEGINNER, COMPLEXITY_INTERMEDIATE},
        "allowed_entity_types": {ENTITY_TYPE_PRACTICE, ENTITY_TYPE_HABIT, ENTITY_TYPE_RITUAL},
        "max_duration_minutes": 30,
        "safety_gated": False,
    },
    "explorer": {
        "allowed_complexity_levels": {COMPLEXITY_INTERMEDIATE},
        "allowed_entity_types": {
            ENTITY_TYPE_PRACTICE,
            ENTITY_TYPE_HABIT,
            ENTITY_TYPE_RITUAL,
            ENTITY_TYPE_CYCLE,
        },
        "max_duration_minutes": 45,
        "safety_gated": False,
    },
    "architect": {
        "allowed_complexity_levels": {
            COMPLEXITY_BEGINNER,
            COMPLEXITY_INTERMEDIATE,
            COMPLEXITY_ADVANCED,
        },
        "allowed_entity_types": {
            ENTITY_TYPE_PRACTICE,
            ENTITY_TYPE_HABIT,
            ENTITY_TYPE_RITUAL,
            ENTITY_TYPE_CYCLE,
        },
        "max_duration_minutes": 60,
        "safety_gated": False,
    },
    "mentor": {
        "allowed_complexity_levels": {
            COMPLEXITY_BEGINNER,
            COMPLEXITY_INTERMEDIATE,
            COMPLEXITY_ADVANCED,
        },
        "allowed_entity_types": {
            ENTITY_TYPE_PRACTICE,
            ENTITY_TYPE_HABIT,
            ENTITY_TYPE_RITUAL,
            ENTITY_TYPE_CYCLE,
        },
        "max_duration_minutes": 90,
        "safety_gated": True,
    },
    "master": {
        "allowed_complexity_levels": {
            COMPLEXITY_BEGINNER,
            COMPLEXITY_INTERMEDIATE,
            COMPLEXITY_ADVANCED,
        },
        "allowed_entity_types": {
            ENTITY_TYPE_PRACTICE,
            ENTITY_TYPE_HABIT,
            ENTITY_TYPE_RITUAL,
            ENTITY_TYPE_CYCLE,
        },
        "max_duration_minutes": 90,
        "safety_gated": True,
    },
}

EVOLUTION_PRACTICE_SELECTOR_FILTER_V1_KEYS = frozenset(
    {
        "contract_version",
        "filter_id",
        "source_evolution_slice_id",
        "evolution_stage",
        "allowed_complexity_levels",
        "allowed_path_themes",
        "max_duration_minutes",
        "allowed_entity_types",
        "filtered_candidates",
        "blocked_candidates",
        "safety_notes_required",
        "selection_performed",
        "recommendation_created",
        "created_at",
    }
)


class EvolutionPracticeSelectorFilterError(ValueError):
    """Raised when practice selector filter inputs are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_practice_selector_filter_id() -> str:
    return f"epsf-{uuid4()}"


def _is_valid_practice_selector_slice(
    evolution_slice: dict[str, Any],
) -> tuple[bool, str | None]:
    if evolution_slice.get("contract_version") == EVOLUTION_EFFECT_RUNTIME_POLICY_V1_CONTRACT:
        return False, "full_policy_not_accepted"
    if evolution_slice.get("contract_version") != EVOLUTION_EFFECT_CONSUMER_SLICE_V1_CONTRACT:
        return False, "invalid_slice_contract"
    if evolution_slice.get("consumer_id") != CONSUMER_PRACTICE_SELECTOR:
        return False, "invalid_consumer_id"
    errors = validate_evolution_effect_consumer_slice_v1(
        evolution_slice,
        consumer_id=CONSUMER_PRACTICE_SELECTOR,
    )
    if errors:
        return False, "invalid_slice_payload"
    return True, None


def resolve_practice_selector_limits_from_slice_v1(
    evolution_slice: dict[str, Any],
    *,
    path_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve stage-safe practice selector limits from a validated practice_selector slice."""
    valid, reason = _is_valid_practice_selector_slice(evolution_slice)
    if not valid:
        raise EvolutionPracticeSelectorFilterError(reason or "invalid evolution slice")

    stage = str(evolution_slice.get("current_stage") or "seeker")
    profile = STAGE_PRACTICE_LIMITS.get(stage, STAGE_PRACTICE_LIMITS["seeker"])

    limits = evolution_slice.get("effect_limits") or {}
    unlock = (evolution_slice.get("allowed_effects") or {}).get("unlock_effects") or {}

    practice_pack_tier = limits.get("practice_pack_tier") or unlock.get("practice_pack_tier") or "starter"
    cycle_lengths = limits.get("cycle_lengths_available") or unlock.get("cycle_lengths_available") or [7]
    path_themes_max_active = int(
        limits.get("path_themes_max_active") or unlock.get("path_themes_max_active") or 1
    )

    ctx = path_context or {}
    candidate_themes = list(ctx.get("active_path_themes") or ctx.get("allowed_path_themes") or [])
    allowed_path_themes = candidate_themes[:path_themes_max_active]

    allowed_complexity = set(profile["allowed_complexity_levels"])
    pack_max = PACK_TIER_MAX_COMPLEXITY.get(str(practice_pack_tier), COMPLEXITY_BEGINNER)
    pack_max_order = COMPLEXITY_ORDER[pack_max]
    allowed_complexity = {
        level for level in allowed_complexity if COMPLEXITY_ORDER[level] <= pack_max_order
    }

    return {
        "evolution_stage": stage,
        "source_evolution_slice_id": evolution_slice.get("slice_id"),
        "allowed_complexity_levels": sorted(
            allowed_complexity,
            key=lambda level: COMPLEXITY_ORDER[level],
        ),
        "allowed_path_themes": allowed_path_themes,
        "max_duration_minutes": int(profile["max_duration_minutes"]),
        "allowed_entity_types": sorted(profile["allowed_entity_types"]),
        "cycle_lengths_available": [int(value) for value in cycle_lengths],
        "practice_pack_tier": str(practice_pack_tier),
        "safety_notes_required": bool(profile["safety_gated"]),
    }


def _candidate_id(candidate: dict[str, Any]) -> str:
    if candidate.get("candidate_id"):
        return str(candidate["candidate_id"])
    entity_type = candidate.get("entity_type", "practice")
    code = candidate.get("code", "unknown")
    return f"{entity_type}:{code}"


def _evaluate_candidate(
    candidate: dict[str, Any],
    limits: dict[str, Any],
) -> tuple[bool, str | None]:
    if candidate.get("has_definition") is False:
        return False, BLOCK_MISSING_DEFINITION

    entity_type = str(candidate.get("entity_type") or "")
    if entity_type not in ALLOWED_ENTITY_TYPES:
        return False, BLOCK_MISSING_DEFINITION

    if entity_type not in set(limits["allowed_entity_types"]):
        return False, BLOCK_ENTITY_TYPE_NOT_ALLOWED

    complexity = str(candidate.get("complexity_level") or COMPLEXITY_BEGINNER)
    if complexity not in COMPLEXITY_ORDER:
        return False, BLOCK_MISSING_DEFINITION
    if complexity not in set(limits["allowed_complexity_levels"]):
        return False, BLOCK_COMPLEXITY_ABOVE_STAGE

    pack_tier = candidate.get("practice_pack_tier")
    if pack_tier is not None:
        allowed_pack = limits.get("practice_pack_tier", "starter")
        if PACK_TIER_ORDER.get(str(pack_tier), 0) > PACK_TIER_ORDER.get(str(allowed_pack), 0):
            return False, BLOCK_COMPLEXITY_ABOVE_STAGE

    path_themes = candidate.get("path_themes") or []
    if not isinstance(path_themes, list):
        return False, BLOCK_MISSING_DEFINITION
    allowed_themes = set(limits.get("allowed_path_themes") or [])
    if allowed_themes and not (set(path_themes) & allowed_themes):
        return False, BLOCK_PATH_THEME_NOT_ALLOWED

    duration_minutes = int(candidate.get("duration_minutes") or 0)
    if duration_minutes > int(limits["max_duration_minutes"]):
        return False, BLOCK_DURATION_ABOVE_CAP

    if entity_type == ENTITY_TYPE_CYCLE:
        cycle_days = candidate.get("cycle_length_days")
        if cycle_days is not None:
            available = set(limits.get("cycle_lengths_available") or [])
            if available and int(cycle_days) not in available:
                return False, BLOCK_DURATION_ABOVE_CAP

    if limits.get("safety_notes_required") and candidate.get("safety_note_required") is True:
        return False, BLOCK_SAFETY_NOTE_REQUIRED

    return True, None


def build_evolution_practice_selector_filter_v1(
    practice_candidates: list[dict[str, Any]],
    *,
    evolution_slice: dict[str, Any] | None = None,
    path_context: dict[str, Any] | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """
    Apply B1.7 practice_selector slice as cap/filter layer on practice candidates.

    Evolution can limit practice complexity but cannot prescribe a practice.
    """
    if not isinstance(practice_candidates, list):
        raise EvolutionPracticeSelectorFilterError("practice_candidates must be a list")

    filtered: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []

    if evolution_slice is None:
        limits = {
            "evolution_stage": None,
            "source_evolution_slice_id": None,
            "allowed_complexity_levels": sorted(COMPLEXITY_ORDER.keys(), key=COMPLEXITY_ORDER.get),
            "allowed_path_themes": list((path_context or {}).get("active_path_themes") or []),
            "max_duration_minutes": 999,
            "allowed_entity_types": sorted(ALLOWED_ENTITY_TYPES),
            "cycle_lengths_available": [],
            "practice_pack_tier": "full",
            "safety_notes_required": False,
        }
        for candidate in practice_candidates:
            if not isinstance(candidate, dict):
                continue
            if candidate.get("has_definition") is False:
                blocked.append(
                    {
                        "candidate_id": _candidate_id(candidate),
                        "code": candidate.get("code"),
                        "entity_type": candidate.get("entity_type"),
                        "reason": BLOCK_MISSING_DEFINITION,
                    }
                )
                continue
            filtered.append(dict(candidate))
    else:
        valid, invalid_reason = _is_valid_practice_selector_slice(evolution_slice)
        if not valid:
            limits = {
                "evolution_stage": None,
                "source_evolution_slice_id": None,
                "allowed_complexity_levels": sorted(COMPLEXITY_ORDER.keys(), key=COMPLEXITY_ORDER.get),
                "allowed_path_themes": list((path_context or {}).get("active_path_themes") or []),
                "max_duration_minutes": 999,
                "allowed_entity_types": sorted(ALLOWED_ENTITY_TYPES),
                "cycle_lengths_available": [],
                "practice_pack_tier": "full",
                "safety_notes_required": False,
            }
            for candidate in practice_candidates:
                if not isinstance(candidate, dict):
                    continue
                if candidate.get("has_definition") is False:
                    blocked.append(
                        {
                            "candidate_id": _candidate_id(candidate),
                            "code": candidate.get("code"),
                            "entity_type": candidate.get("entity_type"),
                            "reason": BLOCK_MISSING_DEFINITION,
                        }
                    )
                    continue
                filtered.append(dict(candidate))
        else:
            limits = resolve_practice_selector_limits_from_slice_v1(
                evolution_slice,
                path_context=path_context,
            )
            for candidate in practice_candidates:
                if not isinstance(candidate, dict):
                    continue
                allowed, reason = _evaluate_candidate(candidate, limits)
                entry = {
                    "candidate_id": _candidate_id(candidate),
                    "code": candidate.get("code"),
                    "entity_type": candidate.get("entity_type"),
                }
                if allowed:
                    filtered.append(dict(candidate))
                else:
                    blocked.append({**entry, "reason": reason})

    result = {
        "contract_version": EVOLUTION_PRACTICE_SELECTOR_FILTER_V1_CONTRACT,
        "filter_id": generate_practice_selector_filter_id(),
        "source_evolution_slice_id": limits.get("source_evolution_slice_id"),
        "evolution_stage": limits.get("evolution_stage"),
        "allowed_complexity_levels": list(limits.get("allowed_complexity_levels") or []),
        "allowed_path_themes": list(limits.get("allowed_path_themes") or []),
        "max_duration_minutes": limits.get("max_duration_minutes"),
        "allowed_entity_types": list(limits.get("allowed_entity_types") or []),
        "filtered_candidates": filtered,
        "blocked_candidates": blocked,
        "safety_notes_required": bool(limits.get("safety_notes_required")),
        "selection_performed": False,
        "recommendation_created": False,
        "created_at": created_at or _utc_now_iso(),
    }

    errors = validate_evolution_practice_selector_filter_v1(result)
    if errors:
        raise EvolutionPracticeSelectorFilterError("; ".join(errors))

    return result


def validate_evolution_practice_selector_filter_v1(filter_result: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if filter_result.get("contract_version") != EVOLUTION_PRACTICE_SELECTOR_FILTER_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in EVOLUTION_PRACTICE_SELECTOR_FILTER_V1_KEYS:
        if key not in filter_result:
            errors.append(f"missing field: {key}")

    if filter_result.get("selection_performed") is not False:
        errors.append("selection_performed must be false")
    if filter_result.get("recommendation_created") is not False:
        errors.append("recommendation_created must be false")

    if not isinstance(filter_result.get("filtered_candidates"), list):
        errors.append("filtered_candidates must be array")
    if not isinstance(filter_result.get("blocked_candidates"), list):
        errors.append("blocked_candidates must be array")
    if not isinstance(filter_result.get("allowed_complexity_levels"), list):
        errors.append("allowed_complexity_levels must be array")
    if not isinstance(filter_result.get("allowed_path_themes"), list):
        errors.append("allowed_path_themes must be array")
    if not isinstance(filter_result.get("allowed_entity_types"), list):
        errors.append("allowed_entity_types must be array")

    forbidden = set(filter_result.keys()) & {
        "vector",
        "strategy",
        "risk",
        "tempo",
        "source_weights",
        "recommendation",
        "commerce",
        "stage_update",
        "llm_call",
        "blocked_effects",
        "allowed_effects",
        "effect_limits",
    }
    if forbidden:
        errors.append(f"forbidden fields on filter result: {sorted(forbidden)}")

    extra = set(filter_result.keys()) - EVOLUTION_PRACTICE_SELECTOR_FILTER_V1_KEYS
    if extra:
        errors.append(f"unexpected fields: {sorted(extra)}")

    return errors
