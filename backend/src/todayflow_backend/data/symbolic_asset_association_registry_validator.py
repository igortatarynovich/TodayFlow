"""D1.2 — Validate Symbolic Asset Association registry (links only, not recommendations)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from todayflow_backend.data.cycle_definition_registry_validator import (
    CANONICAL_CYCLE_DEFINITION_CODES,
)
from todayflow_backend.data.evolution_cd_validator import CANONICAL_STAGE_ORDER
from todayflow_backend.data.practice_definition_registry_validator import (
    CANONICAL_PRACTICE_CATEGORIES,
)
from todayflow_backend.data.reference_machine_loader import VECTOR_AXIS_KEYS
from todayflow_backend.services.calendar_rhythm_pattern_candidate_v1 import (
    ALLOWED_CANDIDATE_TYPES,
)
from todayflow_backend.services.day_model_v1_interpreter import (
    RISK_CLASS_VALUES,
    STRATEGY_VALUES,
    TEMPO_INSTRUCTION_VALUES,
)

SYMBOLIC_ASSET_ASSOCIATION_REGISTRY_V1_CONTRACT = (
    "symbolic_asset_association_registry_v1"
)

SYMBOLIC_ASSET_ASSOCIATION_V1_CONTRACT = "symbolic_asset_association_v1"

ALLOWED_REGISTRY_STATUSES = frozenset({"draft", "active"})

ALLOWED_ASSOCIATION_STATUSES = frozenset({"draft", "active"})

ALLOWED_ASSOCIATION_TYPES = frozenset(
    {
        "daymodel",
        "path",
        "cycle",
        "rhythm",
        "practice",
        "knowledge",
        "evolution",
    }
)

ALLOWED_ASSOCIATION_MODES = frozenset(
    {
        "supports",
        "balances",
        "amplifies",
        "grounds",
        "reflects",
    }
)

DAYMODEL_TARGET_PREFIXES = frozenset({"strategy", "risk", "tempo", "vector"})

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

TARGET_REF_PATTERN = re.compile(r"^[a-z][a-z0-9_]*:[a-z0-9_.-]+$")

MACHINE_CLAIM_PATTERN = re.compile(r"^[a-z_]+:[a-z0-9_.-]+$")

FORBIDDEN_TEXT_PATTERN = re.compile(
    r"(recommend|purchase|buy_now|needed_for|fixes|heals|diagnos|medical|"
    r"financial|psychological|user_id|personalized|sales_copy|ui_copy|"
    r"you_should|must_buy|shop_now|sku|inventory|price)",
    re.I,
)

FORBIDDEN_ASSOCIATION_FIELDS = frozenset(
    {
        "recommendation",
        "recommendation_id",
        "recommendations",
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
    }
)

SYMBOLIC_ASSET_ASSOCIATION_V1_KEYS = frozenset(
    {
        "contract_version",
        "association_id",
        "asset_code",
        "association_type",
        "target_ref",
        "strength",
        "confidence",
        "association_mode",
        "status",
        "version",
    }
)

SYMBOLIC_ASSET_ASSOCIATION_REGISTRY_V1_TOP_KEYS = frozenset(
    {
        "contract_version",
        "domain",
        "version",
        "status",
        "description",
        "symbolic_asset_associations",
    }
)

MIN_CANONICAL_ASSOCIATION_COUNT = 60
MAX_CANONICAL_ASSOCIATION_COUNT = 100


@dataclass(frozen=True)
class SymbolicAssetAssociationValidationContext:
    asset_codes: frozenset[str]
    path_theme_codes: frozenset[str]
    evolution_stage_codes: frozenset[str]
    practice_codes: frozenset[str]
    cycle_codes: frozenset[str]
    rhythm_pattern_types: frozenset[str]
    strategy_codes: frozenset[str]
    risk_codes: frozenset[str]
    tempo_codes: frozenset[str]
    vector_axes: frozenset[str]
    knowledge_claim_prefixes: frozenset[str]


def default_validation_context(
    *,
    asset_codes: frozenset[str],
    path_theme_codes: frozenset[str],
) -> SymbolicAssetAssociationValidationContext:
    return SymbolicAssetAssociationValidationContext(
        asset_codes=asset_codes,
        path_theme_codes=path_theme_codes,
        evolution_stage_codes=frozenset(CANONICAL_STAGE_ORDER),
        practice_codes=frozenset(CANONICAL_PRACTICE_CATEGORIES),
        cycle_codes=frozenset(CANONICAL_CYCLE_DEFINITION_CODES),
        rhythm_pattern_types=frozenset(ALLOWED_CANDIDATE_TYPES),
        strategy_codes=frozenset(STRATEGY_VALUES),
        risk_codes=frozenset(RISK_CLASS_VALUES),
        tempo_codes=frozenset(TEMPO_INSTRUCTION_VALUES),
        vector_axes=frozenset(VECTOR_AXIS_KEYS),
        knowledge_claim_prefixes=ALLOWED_KNOWLEDGE_CLAIM_PREFIXES,
    )


class SymbolicAssetAssociationRegistryValidationError(Exception):
    """Raised when symbolic asset association registry payload fails validation."""


def _validate_strength_confidence(value: Any, *, field: str, label: str) -> list[str]:
    if not isinstance(value, (int, float)):
        return [f"{label}: {field} must be number"]
    if value < 0 or value > 1:
        return [f"{label}: {field} must be between 0 and 1"]
    return []


def _validate_target_ref_for_type(
    association_type: str,
    target_ref: str,
    *,
    context: SymbolicAssetAssociationValidationContext,
    label: str,
) -> list[str]:
    errors: list[str] = []

    if association_type == "knowledge":
        if not MACHINE_CLAIM_PATTERN.match(target_ref):
            errors.append(f"{label}: knowledge target_ref must be prefix:value claim")
            return errors
        prefix, _value = target_ref.split(":", 1)
        if prefix not in context.knowledge_claim_prefixes:
            errors.append(f"{label}: invalid knowledge claim prefix {prefix!r}")
        return errors

    if not TARGET_REF_PATTERN.match(target_ref):
        errors.append(f"{label}: target_ref must be namespace:code")
        return errors

    namespace, code = target_ref.split(":", 1)

    if association_type == "path":
        if namespace != "path":
            errors.append(f"{label}: path association requires path: namespace")
        elif code not in context.path_theme_codes:
            errors.append(f"{label}: invalid path theme {code!r}")
    elif association_type == "evolution":
        if namespace != "stage":
            errors.append(f"{label}: evolution association requires stage: namespace")
        elif code not in context.evolution_stage_codes:
            errors.append(f"{label}: invalid evolution stage {code!r}")
    elif association_type == "practice":
        if namespace != "practice":
            errors.append(f"{label}: practice association requires practice: namespace")
        elif code not in context.practice_codes:
            errors.append(f"{label}: invalid practice code {code!r}")
    elif association_type == "cycle":
        if namespace != "cycle":
            errors.append(f"{label}: cycle association requires cycle: namespace")
        elif code not in context.cycle_codes:
            errors.append(f"{label}: invalid cycle code {code!r}")
    elif association_type == "rhythm":
        if namespace != "rhythm":
            errors.append(f"{label}: rhythm association requires rhythm: namespace")
        elif code not in context.rhythm_pattern_types:
            errors.append(f"{label}: invalid rhythm pattern type {code!r}")
    elif association_type == "daymodel":
        if namespace not in DAYMODEL_TARGET_PREFIXES:
            errors.append(f"{label}: invalid daymodel namespace {namespace!r}")
        elif namespace == "strategy" and code not in context.strategy_codes:
            errors.append(f"{label}: invalid strategy code {code!r}")
        elif namespace == "risk" and code not in context.risk_codes:
            errors.append(f"{label}: invalid risk code {code!r}")
        elif namespace == "tempo" and code not in context.tempo_codes:
            errors.append(f"{label}: invalid tempo code {code!r}")
        elif namespace == "vector" and code not in context.vector_axes:
            errors.append(f"{label}: invalid vector axis {code!r}")
    else:
        errors.append(f"{label}: unsupported association_type {association_type!r}")

    return errors


def validate_symbolic_asset_association_v1(
    association: dict[str, Any],
    *,
    context: SymbolicAssetAssociationValidationContext,
    prefix: str = "",
) -> list[str]:
    errors: list[str] = []
    label = prefix or "symbolic_asset_association"

    if association.get("contract_version") != SYMBOLIC_ASSET_ASSOCIATION_V1_CONTRACT:
        errors.append(f"{label}: invalid contract_version")

    for key in SYMBOLIC_ASSET_ASSOCIATION_V1_KEYS:
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

    asset_code = association.get("asset_code")
    if not isinstance(asset_code, str) or not asset_code:
        errors.append(f"{label}: asset_code required")
    elif asset_code not in context.asset_codes:
        errors.append(f"{label}: asset_code {asset_code!r} not in D1.1 registry")

    association_type = association.get("association_type")
    if association_type not in ALLOWED_ASSOCIATION_TYPES:
        errors.append(f"{label}: invalid association_type")

    target_ref = association.get("target_ref")
    if not isinstance(target_ref, str) or not target_ref.strip():
        errors.append(f"{label}: target_ref required")
    elif FORBIDDEN_TEXT_PATTERN.search(target_ref):
        errors.append(f"{label}: target_ref contains forbidden language")
    elif isinstance(association_type, str):
        errors.extend(
            _validate_target_ref_for_type(
                association_type,
                target_ref,
                context=context,
                label=label,
            )
        )

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

    if association.get("association_mode") not in ALLOWED_ASSOCIATION_MODES:
        errors.append(f"{label}: invalid association_mode")

    if association.get("status") not in ALLOWED_ASSOCIATION_STATUSES:
        errors.append(f"{label}: invalid status")

    version = association.get("version")
    if not isinstance(version, str) or not version.strip():
        errors.append(f"{label}: version required")

    for text_field in ("association_id", "target_ref"):
        value = association.get(text_field)
        if isinstance(value, str) and FORBIDDEN_TEXT_PATTERN.search(value):
            errors.append(f"{label}: {text_field} contains forbidden language")

    return errors


def validate_symbolic_asset_association_registry_v1(
    payload: dict[str, Any],
    *,
    context: SymbolicAssetAssociationValidationContext,
) -> list[str]:
    errors: list[str] = []

    if payload.get("contract_version") != SYMBOLIC_ASSET_ASSOCIATION_REGISTRY_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in SYMBOLIC_ASSET_ASSOCIATION_REGISTRY_V1_TOP_KEYS:
        if key not in payload:
            errors.append(f"missing top-level field: {key}")

    if payload.get("domain") != "symbolic":
        errors.append("domain must be symbolic")

    if payload.get("status") not in ALLOWED_REGISTRY_STATUSES:
        errors.append("invalid top-level status")

    associations = payload.get("symbolic_asset_associations")
    if not isinstance(associations, dict):
        errors.append("symbolic_asset_associations must be object")
        return errors

    count = len(associations)
    if count < MIN_CANONICAL_ASSOCIATION_COUNT:
        errors.append(
            f"symbolic_asset_associations must include >= {MIN_CANONICAL_ASSOCIATION_COUNT} links"
        )
    if count > MAX_CANONICAL_ASSOCIATION_COUNT:
        errors.append(
            f"symbolic_asset_associations must include <= {MAX_CANONICAL_ASSOCIATION_COUNT} links"
        )

    seen_ids: set[str] = set()
    for assoc_id, entry in associations.items():
        prefix = f"symbolic_asset_association[{assoc_id}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: must be object")
            continue

        if assoc_id in seen_ids:
            errors.append(f"duplicate association_id key: {assoc_id!r}")
        seen_ids.add(assoc_id)

        entry_errors = validate_symbolic_asset_association_v1(
            entry,
            context=context,
            prefix=prefix,
        )
        errors.extend(entry_errors)

        if entry.get("association_id") != assoc_id:
            errors.append(f"{prefix}: association_id must match registry key")

    if len(seen_ids) != len(associations):
        errors.append("association_id keys must be unique")

    return errors
