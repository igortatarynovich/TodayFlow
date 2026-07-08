"""D1.3 — Validate Symbolic Collection registry (curated groups, not shop bundles)."""

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
from todayflow_backend.data.symbolic_asset_definition_registry_validator import (
    ALLOWED_SYMBOLIC_THEME_CODES,
)
from todayflow_backend.services.calendar_rhythm_pattern_candidate_v1 import (
    ALLOWED_CANDIDATE_TYPES,
)

SYMBOLIC_COLLECTION_REGISTRY_V1_CONTRACT = "symbolic_collection_registry_v1"

SYMBOLIC_COLLECTION_V1_CONTRACT = "symbolic_collection_v1"

ALLOWED_REGISTRY_STATUSES = frozenset({"draft", "active"})

ALLOWED_COLLECTION_STATUSES = frozenset({"draft", "active"})

ALLOWED_COLLECTION_TYPES = frozenset(
    {
        "path",
        "cycle",
        "rhythm",
        "stage",
        "practice",
        "theme",
    }
)

ALLOWED_COLLECTION_VISIBILITY_TIERS = frozenset({"none", "soft", "standard", "full"})

COMPATIBLE_CONTEXT_NAMESPACES = frozenset(
    {
        "path",
        "stage",
        "cycle",
        "rhythm",
        "practice",
    }
)

COLLECTION_CODE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

INTERPRETIVE_COLLECTION_CODE_PATTERN = re.compile(
    r"(_for_|^abundance_|^success_|_anxiety$|_love$|_bundle$|shop_|buy_)",
    re.I,
)

COMPATIBLE_CONTEXT_PATTERN = re.compile(r"^[a-z][a-z0-9_]*:[a-z0-9_.-]+$")

FORBIDDEN_TEXT_PATTERN = re.compile(
    r"(recommend|purchase|buy_now|needed_for|fixes|heals|diagnos|medical|"
    r"financial|psychological|user_id|personalized|sales_copy|ui_copy|"
    r"you_should|must_buy|shop_now|sku|inventory|price|product_bundle|"
    r"purchase_cta|bundle_price|add_to_cart)",
    re.I,
)

FORBIDDEN_COLLECTION_FIELDS = frozenset(
    {
        "recommendation",
        "recommendation_id",
        "recommendations",
        "user_id",
        "profile_id",
        "personalized",
        "personalization",
        "personalized_reason",
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
        "product_bundle",
        "bundle_sku",
        "price",
        "pricing",
        "inventory",
        "stock",
        "checkout",
        "purchase",
        "purchase_cta",
        "buy",
        "offer",
        "targeting",
        "llm_output",
    }
)

SYMBOLIC_COLLECTION_V1_KEYS = frozenset(
    {
        "contract_version",
        "collection_code",
        "title",
        "collection_type",
        "asset_codes",
        "primary_theme_codes",
        "association_refs",
        "compatible_contexts",
        "visibility_tier",
        "status",
        "version",
    }
)

SYMBOLIC_COLLECTION_REGISTRY_V1_TOP_KEYS = frozenset(
    {
        "contract_version",
        "domain",
        "version",
        "status",
        "description",
        "symbolic_collections",
    }
)

MIN_CANONICAL_COLLECTION_COUNT = 10
MAX_CANONICAL_COLLECTION_COUNT = 16

COLLECTION_TYPE_CONTEXT_NAMESPACE = {
    "path": "path",
    "stage": "stage",
    "cycle": "cycle",
    "rhythm": "rhythm",
    "practice": "practice",
}


@dataclass(frozen=True)
class SymbolicCollectionValidationContext:
    asset_codes: frozenset[str]
    association_ids: frozenset[str]
    path_theme_codes: frozenset[str]
    evolution_stage_codes: frozenset[str]
    practice_codes: frozenset[str]
    cycle_codes: frozenset[str]
    rhythm_pattern_types: frozenset[str]


class SymbolicCollectionRegistryValidationError(Exception):
    """Raised when symbolic collection registry payload fails validation."""


def _validate_compatible_context(
    context_ref: str,
    *,
    validation_context: SymbolicCollectionValidationContext,
    label: str,
) -> list[str]:
    errors: list[str] = []
    if not COMPATIBLE_CONTEXT_PATTERN.match(context_ref):
        errors.append(f"{label}: compatible_context must be namespace:code")
        return errors

    namespace, code = context_ref.split(":", 1)
    if namespace not in COMPATIBLE_CONTEXT_NAMESPACES:
        errors.append(f"{label}: invalid compatible_context namespace {namespace!r}")
        return errors

    if namespace == "path" and code not in validation_context.path_theme_codes:
        errors.append(f"{label}: invalid path context {code!r}")
    elif namespace == "stage" and code not in validation_context.evolution_stage_codes:
        errors.append(f"{label}: invalid stage context {code!r}")
    elif namespace == "cycle" and code not in validation_context.cycle_codes:
        errors.append(f"{label}: invalid cycle context {code!r}")
    elif namespace == "rhythm" and code not in validation_context.rhythm_pattern_types:
        errors.append(f"{label}: invalid rhythm context {code!r}")
    elif namespace == "practice" and code not in validation_context.practice_codes:
        errors.append(f"{label}: invalid practice context {code!r}")

    return errors


def validate_symbolic_collection_v1(
    collection: dict[str, Any],
    *,
    context: SymbolicCollectionValidationContext,
    prefix: str = "",
) -> list[str]:
    errors: list[str] = []
    label = prefix or "symbolic_collection"

    if collection.get("contract_version") != SYMBOLIC_COLLECTION_V1_CONTRACT:
        errors.append(f"{label}: invalid contract_version")

    for key in SYMBOLIC_COLLECTION_V1_KEYS:
        if key not in collection:
            errors.append(f"{label}: missing field {key!r}")

    forbidden = set(collection.keys()) & FORBIDDEN_COLLECTION_FIELDS
    if forbidden:
        errors.append(f"{label}: forbidden fields: {sorted(forbidden)}")

    collection_code = collection.get("collection_code")
    if not isinstance(collection_code, str) or not collection_code:
        errors.append(f"{label}: collection_code required")
    elif not COLLECTION_CODE_PATTERN.match(collection_code):
        errors.append(f"{label}: collection_code must be snake_case")
    elif INTERPRETIVE_COLLECTION_CODE_PATTERN.search(collection_code):
        errors.append(f"{label}: collection_code must name grouping, not offer")

    title = collection.get("title")
    if not isinstance(title, str) or not title.strip():
        errors.append(f"{label}: title required")
    elif FORBIDDEN_TEXT_PATTERN.search(title):
        errors.append(f"{label}: title contains forbidden language")

    collection_type = collection.get("collection_type")
    if collection_type not in ALLOWED_COLLECTION_TYPES:
        errors.append(f"{label}: invalid collection_type")

    asset_codes = collection.get("asset_codes")
    if not isinstance(asset_codes, list) or not asset_codes:
        errors.append(f"{label}: asset_codes must be non-empty array")
    elif len(asset_codes) != len(set(asset_codes)):
        errors.append(f"{label}: asset_codes must be unique")
    else:
        for asset_code in asset_codes:
            if not isinstance(asset_code, str):
                errors.append(f"{label}: asset_codes must be strings")
            elif asset_code not in context.asset_codes:
                errors.append(f"{label}: asset_code {asset_code!r} not in D1.1 registry")

    theme_codes = collection.get("primary_theme_codes")
    if not isinstance(theme_codes, list) or not theme_codes:
        errors.append(f"{label}: primary_theme_codes must be non-empty array")
    elif len(theme_codes) != len(set(theme_codes)):
        errors.append(f"{label}: primary_theme_codes must be unique")
    else:
        for theme in theme_codes:
            if theme not in ALLOWED_SYMBOLIC_THEME_CODES:
                errors.append(f"{label}: invalid primary_theme_code {theme!r}")

    association_refs = collection.get("association_refs")
    if not isinstance(association_refs, list):
        errors.append(f"{label}: association_refs must be array")
    else:
        if len(association_refs) != len(set(association_refs)):
            errors.append(f"{label}: association_refs must be unique")
        for assoc_id in association_refs:
            if not isinstance(assoc_id, str):
                errors.append(f"{label}: association_refs must be strings")
            elif assoc_id not in context.association_ids:
                errors.append(f"{label}: association_ref {assoc_id!r} not in D1.2 registry")

    compatible_contexts = collection.get("compatible_contexts")
    if not isinstance(compatible_contexts, list):
        errors.append(f"{label}: compatible_contexts must be array")
    else:
        if len(compatible_contexts) != len(set(compatible_contexts)):
            errors.append(f"{label}: compatible_contexts must be unique")
        for context_ref in compatible_contexts:
            if not isinstance(context_ref, str):
                errors.append(f"{label}: compatible_contexts must be strings")
            elif FORBIDDEN_TEXT_PATTERN.search(context_ref):
                errors.append(f"{label}: compatible_context contains forbidden language")
            else:
                errors.extend(
                    _validate_compatible_context(
                        context_ref,
                        validation_context=context,
                        label=label,
                    )
                )

        if isinstance(collection_type, str) and collection_type in COLLECTION_TYPE_CONTEXT_NAMESPACE:
            expected_ns = COLLECTION_TYPE_CONTEXT_NAMESPACE[collection_type]
            if not any(
                isinstance(ref, str) and ref.startswith(f"{expected_ns}:")
                for ref in compatible_contexts
            ):
                errors.append(
                    f"{label}: {collection_type} collection requires compatible_context "
                    f"with {expected_ns}: namespace"
                )

    if collection.get("visibility_tier") not in ALLOWED_COLLECTION_VISIBILITY_TIERS:
        errors.append(f"{label}: invalid visibility_tier")

    if collection.get("status") not in ALLOWED_COLLECTION_STATUSES:
        errors.append(f"{label}: invalid status")

    version = collection.get("version")
    if not isinstance(version, str) or not version.strip():
        errors.append(f"{label}: version required")

    for text_field in ("collection_code", "title"):
        value = collection.get(text_field)
        if isinstance(value, str) and FORBIDDEN_TEXT_PATTERN.search(value):
            errors.append(f"{label}: {text_field} contains forbidden language")

    return errors


def validate_symbolic_collection_registry_v1(
    payload: dict[str, Any],
    *,
    context: SymbolicCollectionValidationContext,
) -> list[str]:
    errors: list[str] = []

    if payload.get("contract_version") != SYMBOLIC_COLLECTION_REGISTRY_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in SYMBOLIC_COLLECTION_REGISTRY_V1_TOP_KEYS:
        if key not in payload:
            errors.append(f"missing top-level field: {key}")

    if payload.get("domain") != "symbolic":
        errors.append("domain must be symbolic")

    if payload.get("status") not in ALLOWED_REGISTRY_STATUSES:
        errors.append("invalid top-level status")

    collections = payload.get("symbolic_collections")
    if not isinstance(collections, dict):
        errors.append("symbolic_collections must be object")
        return errors

    count = len(collections)
    if count < MIN_CANONICAL_COLLECTION_COUNT:
        errors.append(
            f"symbolic_collections must include >= {MIN_CANONICAL_COLLECTION_COUNT} collections"
        )
    if count > MAX_CANONICAL_COLLECTION_COUNT:
        errors.append(
            f"symbolic_collections must include <= {MAX_CANONICAL_COLLECTION_COUNT} collections"
        )

    seen_codes: set[str] = set()
    for code, entry in collections.items():
        prefix = f"symbolic_collection[{code}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: must be object")
            continue

        if code in seen_codes:
            errors.append(f"duplicate collection_code key: {code!r}")
        seen_codes.add(code)

        entry_errors = validate_symbolic_collection_v1(entry, context=context, prefix=prefix)
        errors.extend(entry_errors)

        if entry.get("collection_code") != code:
            errors.append(f"{prefix}: collection_code must match registry key")

    if len(seen_codes) != len(collections):
        errors.append("collection_code keys must be unique")

    return errors
