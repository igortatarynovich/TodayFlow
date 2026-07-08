"""C1.7 — Validate Practice Context Association registry (context links, not selection)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from todayflow_backend.data.evolution_cd_validator import CANONICAL_STAGE_ORDER
from todayflow_backend.data.goal_definition_registry_validator import ALLOWED_GOAL_CATEGORIES
from todayflow_backend.data.practice_definition_registry_validator import (
    CANONICAL_PRACTICE_CATEGORIES,
)
from todayflow_backend.services.calendar_rhythm_pattern_candidate_v1 import (
    ALLOWED_CANDIDATE_TYPES,
)
from todayflow_backend.services.day_model_v1_interpreter import (
    RISK_CLASS_VALUES,
    STRATEGY_VALUES,
    TEMPO_INSTRUCTION_VALUES,
)

PRACTICE_CONTEXT_ASSOCIATION_REGISTRY_V1_CONTRACT = (
    "practice_context_association_registry_v1"
)

PRACTICE_CONTEXT_ASSOCIATION_V1_CONTRACT = "practice_context_association_v1"

ALLOWED_REGISTRY_STATUSES = frozenset({"draft", "active"})

ALLOWED_ASSOCIATION_STATUSES = frozenset({"draft", "active"})

ALLOWED_SOURCE_TYPES = frozenset(
    {
        "daymodel_strategy",
        "daymodel_tempo",
        "daymodel_risk",
        "emotional_load",
        "evolution_stage",
        "path_theme",
        "rhythm_pattern_type",
        "energy_state",
        "mood_state",
        "goal_category",
        "knowledge_claim_prefix",
    }
)

ALLOWED_ASSOCIATION_MODES = frozenset(
    {
        "supports",
        "stabilizes",
        "activates",
        "grounds",
        "reflects",
        "redirects",
        "reduces",
    }
)

ALLOWED_DIRECTIONS = frozenset({"positive", "negative"})

ALLOWED_CONTRAINDICATION_LEVELS = frozenset(
    {"none", "advisory", "moderate", "strict"}
)

EMOTIONAL_LOAD_VALUES = frozenset({"calm", "neutral", "intense"})

ENERGY_STATE_VALUES = frozenset(
    {"low", "moderate", "high", "depleted", "restless"}
)

MOOD_STATE_VALUES = frozenset(
    {"stable", "stressed", "scattered", "low", "flat", "elevated"}
)

ALLOWED_KNOWLEDGE_CLAIM_PREFIXES = frozenset(
    {
        "prefers_content_key_group",
        "responds_to_surface",
        "responds_to_action_mode",
        "responds_to_tempo",
        "risk_response_tolerance",
        "rhythm_energy_weekday",
        "rhythm_mood_weekday",
        "rhythm_completion_weekday",
        "rhythm_recovery_after_overload",
        "rhythm_overload_cluster",
        "rhythm_cycle_month_end",
        "rhythm_practice_streak",
        "rhythm_reflection_weekday",
    }
)

ASSOCIATION_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

SOURCE_REF_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

FORBIDDEN_TEXT_PATTERN = re.compile(
    r"(recommend|purchase|buy_now|needed_for|fixes|heals|diagnos|medical|"
    r"financial|psychological|user_id|personalized|sales_copy|ui_copy|"
    r"you_should|must_buy|shop_now|sku|inventory|price|final_selection|"
    r"select_now|prompt|llm_output)",
    re.I,
)

FORBIDDEN_ASSOCIATION_FIELDS = frozenset(
    {
        "recommendation",
        "recommendation_id",
        "recommendations",
        "final_selection",
        "user_id",
        "profile_id",
        "personalized",
        "personalization",
        "interpretation",
        "interpretations",
        "meaning",
        "meanings",
        "insight",
        "insight_text",
        "ui_copy",
        "sales_copy",
        "display_text",
        "marketing_copy",
        "needed_for",
        "fixes",
        "heals",
        "sku",
        "product_id",
        "product_sku",
        "price",
        "pricing",
        "inventory",
        "stock",
        "checkout",
        "purchase",
        "buy",
        "offer",
        "targeting",
        "llm_output",
        "prompt",
        "prompt_template",
    }
)

PRACTICE_CONTEXT_ASSOCIATION_V1_KEYS = frozenset(
    {
        "contract_version",
        "association_id",
        "source_type",
        "source_ref",
        "practice_definition_code",
        "association_mode",
        "strength",
        "confidence",
        "direction",
        "contraindication_level",
        "status",
        "version",
    }
)

PRACTICE_CONTEXT_ASSOCIATION_REGISTRY_V1_TOP_KEYS = frozenset(
    {
        "contract_version",
        "domain",
        "version",
        "status",
        "description",
        "practice_context_associations",
    }
)

MIN_CANONICAL_ASSOCIATION_COUNT = 80
MAX_CANONICAL_ASSOCIATION_COUNT = 120


@dataclass(frozen=True)
class PracticeContextAssociationValidationContext:
    practice_codes: frozenset[str]
    path_theme_codes: frozenset[str]
    evolution_stage_codes: frozenset[str]
    strategy_codes: frozenset[str]
    risk_codes: frozenset[str]
    tempo_codes: frozenset[str]
    rhythm_pattern_types: frozenset[str]
    goal_categories: frozenset[str]
    knowledge_claim_prefixes: frozenset[str]


def default_validation_context(
    *,
    practice_codes: frozenset[str],
    path_theme_codes: frozenset[str],
) -> PracticeContextAssociationValidationContext:
    return PracticeContextAssociationValidationContext(
        practice_codes=practice_codes,
        path_theme_codes=path_theme_codes,
        evolution_stage_codes=frozenset(CANONICAL_STAGE_ORDER),
        strategy_codes=frozenset(STRATEGY_VALUES),
        risk_codes=frozenset(RISK_CLASS_VALUES),
        tempo_codes=frozenset(TEMPO_INSTRUCTION_VALUES),
        rhythm_pattern_types=frozenset(ALLOWED_CANDIDATE_TYPES),
        goal_categories=frozenset(ALLOWED_GOAL_CATEGORIES),
        knowledge_claim_prefixes=ALLOWED_KNOWLEDGE_CLAIM_PREFIXES,
    )


class PracticeContextAssociationRegistryValidationError(Exception):
    """Raised when practice context association registry payload fails validation."""


def _validate_strength_confidence(value: Any, *, field: str, label: str) -> list[str]:
    if not isinstance(value, (int, float)):
        return [f"{label}: {field} must be number"]
    if value < 0 or value > 1:
        return [f"{label}: {field} must be between 0 and 1"]
    return []


def _validate_source_ref_for_type(
    source_type: str,
    source_ref: str,
    *,
    context: PracticeContextAssociationValidationContext,
    label: str,
) -> list[str]:
    errors: list[str] = []

    if not SOURCE_REF_PATTERN.match(source_ref):
        errors.append(f"{label}: source_ref must be snake_case code")
        return errors

    if source_type == "daymodel_strategy":
        if source_ref not in context.strategy_codes:
            errors.append(f"{label}: invalid strategy code {source_ref!r}")
    elif source_type == "daymodel_tempo":
        if source_ref not in context.tempo_codes:
            errors.append(f"{label}: invalid tempo code {source_ref!r}")
    elif source_type == "daymodel_risk":
        if source_ref not in context.risk_codes:
            errors.append(f"{label}: invalid risk code {source_ref!r}")
    elif source_type == "emotional_load":
        if source_ref not in EMOTIONAL_LOAD_VALUES:
            errors.append(f"{label}: invalid emotional_load {source_ref!r}")
    elif source_type == "evolution_stage":
        if source_ref not in context.evolution_stage_codes:
            errors.append(f"{label}: invalid evolution stage {source_ref!r}")
    elif source_type == "path_theme":
        if source_ref not in context.path_theme_codes:
            errors.append(f"{label}: invalid path theme {source_ref!r}")
    elif source_type == "rhythm_pattern_type":
        if source_ref not in context.rhythm_pattern_types:
            errors.append(f"{label}: invalid rhythm pattern type {source_ref!r}")
    elif source_type == "energy_state":
        if source_ref not in ENERGY_STATE_VALUES:
            errors.append(f"{label}: invalid energy_state {source_ref!r}")
    elif source_type == "mood_state":
        if source_ref not in MOOD_STATE_VALUES:
            errors.append(f"{label}: invalid mood_state {source_ref!r}")
    elif source_type == "goal_category":
        if source_ref not in context.goal_categories:
            errors.append(f"{label}: invalid goal_category {source_ref!r}")
    elif source_type == "knowledge_claim_prefix":
        if source_ref not in context.knowledge_claim_prefixes:
            errors.append(f"{label}: invalid knowledge_claim_prefix {source_ref!r}")
    else:
        errors.append(f"{label}: unsupported source_type {source_type!r}")

    return errors


def validate_practice_context_association_v1(
    association: dict[str, Any],
    *,
    context: PracticeContextAssociationValidationContext,
    prefix: str = "",
) -> list[str]:
    errors: list[str] = []
    label = prefix or "practice_context_association"

    if association.get("contract_version") != PRACTICE_CONTEXT_ASSOCIATION_V1_CONTRACT:
        errors.append(f"{label}: invalid contract_version")

    for key in PRACTICE_CONTEXT_ASSOCIATION_V1_KEYS:
        if key not in association:
            errors.append(f"{label}: missing field {key!r}")

    forbidden = set(association.keys()) & FORBIDDEN_ASSOCIATION_FIELDS
    if forbidden:
        errors.append(f"{label}: forbidden fields: {sorted(forbidden)}")

    association_id = association.get("association_id")
    if not isinstance(association_id, str) or not association_id:
        errors.append(f"{label}: association_id required")
    elif not ASSOCIATION_ID_PATTERN.match(association_id):
        errors.append(f"{label}: association_id must be snake_case")

    source_type = association.get("source_type")
    if source_type not in ALLOWED_SOURCE_TYPES:
        errors.append(f"{label}: invalid source_type")

    source_ref = association.get("source_ref")
    if not isinstance(source_ref, str) or not source_ref.strip():
        errors.append(f"{label}: source_ref required")
    elif FORBIDDEN_TEXT_PATTERN.search(source_ref):
        errors.append(f"{label}: source_ref contains forbidden language")
    elif isinstance(source_type, str):
        errors.extend(
            _validate_source_ref_for_type(
                source_type,
                source_ref,
                context=context,
                label=label,
            )
        )

    practice_code = association.get("practice_definition_code")
    if not isinstance(practice_code, str) or not practice_code:
        errors.append(f"{label}: practice_definition_code required")
    elif practice_code not in context.practice_codes:
        errors.append(f"{label}: practice_definition_code {practice_code!r} not in C1.1")

    if association.get("association_mode") not in ALLOWED_ASSOCIATION_MODES:
        errors.append(f"{label}: invalid association_mode")

    errors.extend(
        _validate_strength_confidence(
            association.get("strength"),
            field="strength",
            label=label,
        )
    )
    errors.extend(
        _validate_strength_confidence(
            association.get("confidence"),
            field="confidence",
            label=label,
        )
    )

    direction = association.get("direction")
    if direction not in ALLOWED_DIRECTIONS:
        errors.append(f"{label}: invalid direction")
        return errors

    contra = association.get("contraindication_level")
    if contra not in ALLOWED_CONTRAINDICATION_LEVELS:
        errors.append(f"{label}: invalid contraindication_level")
    elif direction == "negative":
        if contra not in {"advisory", "moderate", "strict"}:
            errors.append(
                f"{label}: negative direction requires contraindication_level "
                "advisory|moderate|strict"
            )
    elif direction == "positive" and contra != "none":
        errors.append(f"{label}: positive direction requires contraindication_level none")

    if association.get("status") not in ALLOWED_ASSOCIATION_STATUSES:
        errors.append(f"{label}: invalid status")

    version = association.get("version")
    if not isinstance(version, str) or not version.strip():
        errors.append(f"{label}: version required")

    for text_field in ("association_id", "source_ref", "practice_definition_code"):
        value = association.get(text_field)
        if isinstance(value, str) and FORBIDDEN_TEXT_PATTERN.search(value):
            errors.append(f"{label}: {text_field} contains forbidden language")

    return errors


def validate_practice_context_association_registry_v1(
    payload: dict[str, Any],
    *,
    context: PracticeContextAssociationValidationContext,
) -> list[str]:
    errors: list[str] = []

    if payload.get("contract_version") != PRACTICE_CONTEXT_ASSOCIATION_REGISTRY_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in PRACTICE_CONTEXT_ASSOCIATION_REGISTRY_V1_TOP_KEYS:
        if key not in payload:
            errors.append(f"missing top-level field: {key}")

    if payload.get("domain") != "practice":
        errors.append("domain must be practice")

    if payload.get("status") not in ALLOWED_REGISTRY_STATUSES:
        errors.append("invalid top-level status")

    associations = payload.get("practice_context_associations")
    if not isinstance(associations, dict):
        errors.append("practice_context_associations must be object")
        return errors

    count = len(associations)
    if count < MIN_CANONICAL_ASSOCIATION_COUNT:
        errors.append(
            f"practice_context_associations must include >= "
            f"{MIN_CANONICAL_ASSOCIATION_COUNT} links"
        )
    if count > MAX_CANONICAL_ASSOCIATION_COUNT:
        errors.append(
            f"practice_context_associations must include <= "
            f"{MAX_CANONICAL_ASSOCIATION_COUNT} links"
        )

    seen_ids: set[str] = set()
    for assoc_id, entry in associations.items():
        prefix = f"practice_context_association[{assoc_id}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: must be object")
            continue

        if assoc_id in seen_ids:
            errors.append(f"duplicate association_id key: {assoc_id!r}")
        seen_ids.add(assoc_id)

        entry_errors = validate_practice_context_association_v1(
            entry,
            context=context,
            prefix=prefix,
        )
        errors.extend(entry_errors)

        if entry.get("association_id") != assoc_id:
            errors.append(f"{prefix}: association_id must match registry key")

    return errors
