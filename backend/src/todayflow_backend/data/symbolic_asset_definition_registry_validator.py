"""D1.1 — Validate Symbolic Asset Definition registry (objects only, not meanings)."""

from __future__ import annotations

import re
from typing import Any

SYMBOLIC_ASSET_DEFINITION_REGISTRY_V1_CONTRACT = "symbolic_asset_definition_registry_v1"

SYMBOLIC_ASSET_DEFINITION_V1_CONTRACT = "symbolic_asset_definition_v1"

ALLOWED_REGISTRY_STATUSES = frozenset({"draft", "active"})

ALLOWED_DEFINITION_STATUSES = frozenset({"draft", "active"})

CANONICAL_ASSET_CATEGORIES: tuple[str, ...] = (
    "stone",
    "tarot_card",
    "candle",
    "archetype",
    "symbol",
    "color",
    "element",
)

ALLOWED_SYMBOLIC_THEME_CODES = frozenset(
    {
        "discipline",
        "structure",
        "recovery",
        "integration",
        "focus",
        "action",
        "completion",
        "boundary",
        "clarity",
        "energy",
        "healing",
        "spirituality",
        "creativity",
        "relationships",
        "purpose",
        "release",
        "grounding",
        "protection",
        "illumination",
        "transformation",
    }
)

ALLOWED_VISIBILITY_TIERS = frozenset({"reference", "soft", "standard", "full"})

ALLOWED_SYMBOLIC_FAMILIES = frozenset(
    {
        "mineral",
        "major_arcana",
        "ritual_object",
        "mythic_figure",
        "geometric_glyph",
        "chromatic",
        "classical_element",
    }
)

ALLOWED_CULTURAL_ORIGINS = frozenset(
    {
        "universal",
        "western_esoteric",
        "tarot_tradition",
        "cross_cultural",
        "nature_symbolism",
    }
)

ALLOWED_SYMBOLIC_TYPES = frozenset(
    {
        "physical_object",
        "card",
        "flame",
        "archetype_figure",
        "glyph",
        "hue",
        "element",
    }
)

ASSET_CODE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

INTERPRETIVE_ASSET_CODE_PATTERN = re.compile(
    r"(_for_|^abundance_|^success_|_anxiety$|_love$|_wealth$|_prosperity$)",
    re.I,
)

SYMBOLIC_ASSET_DEFINITION_V1_KEYS = frozenset(
    {
        "contract_version",
        "asset_code",
        "asset_name",
        "asset_category",
        "theme_codes",
        "category_code",
        "status",
        "symbolic_family",
        "cultural_origin",
        "symbolic_type",
        "visibility_tier",
        "commerce_eligible",
        "version",
        "created_at",
    }
)

SYMBOLIC_ASSET_DEFINITION_REGISTRY_V1_TOP_KEYS = frozenset(
    {
        "contract_version",
        "domain",
        "version",
        "status",
        "description",
        "symbolic_asset_definitions",
    }
)

FORBIDDEN_DEFINITION_FIELDS = frozenset(
    {
        "daymodel_association",
        "daymodel_associations",
        "day_model_association",
        "path_association",
        "path_associations",
        "cycle_association",
        "cycle_associations",
        "rhythm_association",
        "rhythm_associations",
        "evolution_association",
        "evolution_associations",
        "knowledge_association",
        "knowledge_associations",
        "association",
        "associations",
        "recommendation",
        "recommendation_id",
        "recommendations",
        "interpretation",
        "interpretations",
        "meaning",
        "meanings",
        "meaning_summary",
        "meaning_text",
        "insight",
        "insight_text",
        "llm_output",
        "sku",
        "product_id",
        "product_sku",
        "price",
        "pricing",
        "inventory",
        "stock",
        "checkout",
        "commerce_price",
        "offer",
        "targeting",
    }
)

MIN_CANONICAL_ASSET_COUNT = 30


class SymbolicAssetDefinitionRegistryValidationError(Exception):
    """Raised when symbolic asset definition registry payload fails validation."""


def validate_symbolic_asset_definition_v1(definition: dict[str, Any], *, prefix: str = "") -> list[str]:
    errors: list[str] = []
    label = prefix or "symbolic_asset_definition"

    if definition.get("contract_version") != SYMBOLIC_ASSET_DEFINITION_V1_CONTRACT:
        errors.append(f"{label}: invalid contract_version")

    for key in SYMBOLIC_ASSET_DEFINITION_V1_KEYS:
        if key not in definition:
            errors.append(f"{label}: missing field {key!r}")

    forbidden = set(definition.keys()) & FORBIDDEN_DEFINITION_FIELDS
    if forbidden:
        errors.append(f"{label}: forbidden fields: {sorted(forbidden)}")

    asset_code = definition.get("asset_code")
    if not isinstance(asset_code, str) or not asset_code:
        errors.append(f"{label}: asset_code required")
    elif not ASSET_CODE_PATTERN.match(asset_code):
        errors.append(f"{label}: asset_code must be snake_case")
    elif INTERPRETIVE_ASSET_CODE_PATTERN.search(asset_code):
        errors.append(f"{label}: asset_code must name object, not association")

    asset_name = definition.get("asset_name")
    if not isinstance(asset_name, str) or not asset_name.strip():
        errors.append(f"{label}: asset_name required")

    category_code = definition.get("category_code")
    asset_category = definition.get("asset_category")
    if category_code not in CANONICAL_ASSET_CATEGORIES:
        errors.append(f"{label}: invalid category_code")
    if asset_category not in CANONICAL_ASSET_CATEGORIES:
        errors.append(f"{label}: invalid asset_category")
    if (
        isinstance(category_code, str)
        and isinstance(asset_category, str)
        and category_code != asset_category
    ):
        errors.append(f"{label}: asset_category must match category_code")

    theme_codes = definition.get("theme_codes")
    if not isinstance(theme_codes, list):
        errors.append(f"{label}: theme_codes must be array")
    else:
        if len(theme_codes) != len(set(theme_codes)):
            errors.append(f"{label}: theme_codes must be unique")
        for theme in theme_codes:
            if theme not in ALLOWED_SYMBOLIC_THEME_CODES:
                errors.append(f"{label}: invalid theme_code {theme!r}")

    if definition.get("status") not in ALLOWED_DEFINITION_STATUSES:
        errors.append(f"{label}: invalid status")

    if definition.get("symbolic_family") not in ALLOWED_SYMBOLIC_FAMILIES:
        errors.append(f"{label}: invalid symbolic_family")

    if definition.get("cultural_origin") not in ALLOWED_CULTURAL_ORIGINS:
        errors.append(f"{label}: invalid cultural_origin")

    if definition.get("symbolic_type") not in ALLOWED_SYMBOLIC_TYPES:
        errors.append(f"{label}: invalid symbolic_type")

    if definition.get("visibility_tier") not in ALLOWED_VISIBILITY_TIERS:
        errors.append(f"{label}: invalid visibility_tier")

    if not isinstance(definition.get("commerce_eligible"), bool):
        errors.append(f"{label}: commerce_eligible must be boolean")

    version = definition.get("version")
    if not isinstance(version, str) or not version.strip():
        errors.append(f"{label}: version required")

    created_at = definition.get("created_at")
    if not isinstance(created_at, str) or len(created_at) < 10:
        errors.append(f"{label}: created_at must be ISO timestamp string")

    return errors


def validate_symbolic_asset_definition_registry_v1(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if payload.get("contract_version") != SYMBOLIC_ASSET_DEFINITION_REGISTRY_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in SYMBOLIC_ASSET_DEFINITION_REGISTRY_V1_TOP_KEYS:
        if key not in payload:
            errors.append(f"missing top-level field: {key}")

    if payload.get("domain") != "symbolic":
        errors.append("domain must be symbolic")

    if payload.get("status") not in ALLOWED_REGISTRY_STATUSES:
        errors.append("invalid top-level status")

    definitions = payload.get("symbolic_asset_definitions")
    if not isinstance(definitions, dict):
        errors.append("symbolic_asset_definitions must be object")
        return errors

    if len(definitions) < MIN_CANONICAL_ASSET_COUNT:
        errors.append(f"symbolic_asset_definitions must include >= {MIN_CANONICAL_ASSET_COUNT} assets")

    seen_codes: set[str] = set()
    for code, entry in definitions.items():
        prefix = f"symbolic_asset_definition[{code}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: must be object")
            continue

        if code in seen_codes:
            errors.append(f"duplicate asset_code key: {code!r}")
        seen_codes.add(code)

        entry_errors = validate_symbolic_asset_definition_v1(entry, prefix=prefix)
        errors.extend(entry_errors)

        if entry.get("asset_code") != code:
            errors.append(f"{prefix}: asset_code must match registry key")

    if len(seen_codes) != len(definitions):
        errors.append("asset_code keys must be unique")

    return errors
