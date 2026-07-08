"""D1.4 — Symbolic visibility policy (B1.13 + E1.7 caps on D1.1–D1.3; no recommendation)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.calendar_intelligence_consumer_policy_v1 import (
    BLOCK_CYCLE_VISIBILITY_NOT_ALLOWED,
    BLOCK_RHYTHM_VISIBILITY_NOT_ALLOWED,
    CALENDAR_INTELLIGENCE_CONSUMER_POLICY_V1_CONTRACT,
    validate_calendar_intelligence_consumer_policy_v1,
)
from todayflow_backend.services.evolution_commerce_visibility_policy_v1 import (
    EVOLUTION_COMMERCE_VISIBILITY_POLICY_V1_CONTRACT,
    VISIBILITY_FULL,
    VISIBILITY_NONE,
    VISIBILITY_ORDER,
    VISIBILITY_SOFT,
    VISIBILITY_STANDARD,
    validate_evolution_commerce_visibility_policy_v1,
)

SYMBOLIC_VISIBILITY_POLICY_V1_VERSION = "1.0.0"
SYMBOLIC_VISIBILITY_POLICY_V1_CONTRACT = "symbolic_visibility_policy_v1"

BLOCK_INVALID_COMMERCE_POLICY = "invalid_commerce_policy"
BLOCK_INVALID_CALENDAR_POLICY = "invalid_calendar_policy"
BLOCK_VISIBILITY_NONE = "visibility_none"
BLOCK_ASSETS_ONLY_POLICY = "collections_not_visible_at_soft"
BLOCK_ASSET_CATEGORY_NOT_ALLOWED = "asset_category_not_allowed"
BLOCK_ASSET_TIER_NOT_ALLOWED = "asset_tier_not_allowed"
BLOCK_COLLECTION_TYPE_NOT_VISIBLE = "collection_type_not_visible"

D1_CATEGORY_TO_B13_ASSET_CATEGORY: dict[str, str] = {
    "stone": "stones",
    "candle": "candles",
    "tarot_card": "cards",
    "archetype": "symbolic_sets",
    "symbol": "symbolic_sets",
    "color": "symbolic_sets",
    "element": "symbolic_sets",
}

D1_ASSET_TIER_MIN_VISIBILITY: dict[str, str] = {
    "reference": VISIBILITY_SOFT,
    "soft": VISIBILITY_SOFT,
    "standard": VISIBILITY_STANDARD,
    "full": VISIBILITY_FULL,
}

COLLECTION_TYPE_RHYTHM = "rhythm"
COLLECTION_TYPE_CYCLE = "cycle"

SYMBOLIC_VISIBILITY_POLICY_V1_KEYS = frozenset(
    {
        "contract_version",
        "policy_id",
        "source_commerce_policy_id",
        "source_calendar_consumer_policy_id",
        "visibility_level",
        "visible_assets",
        "visible_collections",
        "redacted_assets",
        "redacted_collections",
        "blocked_assets",
        "blocked_collections",
        "allowed_categories",
        "allowed_collection_types",
        "associations_metadata_allowed",
        "blocked_reasons",
        "recommendation_allowed",
        "commerce_activation_allowed",
        "personalization_allowed",
        "created_at",
        "version",
    }
)

FORBIDDEN_SYMBOLIC_VISIBILITY_FIELDS = frozenset(
    {
        "recommendation",
        "recommendation_id",
        "recommendations",
        "ranking",
        "personalized",
        "personalization",
        "purchase_prompt",
        "offer",
        "sku",
        "pricing",
        "price",
        "targeting",
        "checkout",
        "product_selection",
        "user_id",
        "llm_output",
        "insight",
        "sales_copy",
        "ui_copy",
    }
)


class SymbolicVisibilityPolicyError(ValueError):
    """Raised when symbolic visibility policy inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_symbolic_visibility_policy_id() -> str:
    return f"svp-{uuid4()}"


def _visibility_at_least(level: str, minimum: str) -> bool:
    current = level if level in VISIBILITY_ORDER else VISIBILITY_NONE
    floor = minimum if minimum in VISIBILITY_ORDER else VISIBILITY_NONE
    return VISIBILITY_ORDER[current] >= VISIBILITY_ORDER[floor]


def _normalize_commerce_level(commerce_policy: dict[str, Any]) -> str:
    level = commerce_policy.get("commerce_visibility_level")
    if level in VISIBILITY_ORDER:
        return str(level)
    return VISIBILITY_NONE


def _asset_allowed_by_commerce(
    asset: dict[str, Any],
    *,
    visibility_level: str,
    allowed_asset_categories: list[str],
) -> tuple[bool, str | None]:
    category_code = asset.get("category_code")
    if not isinstance(category_code, str):
        return False, BLOCK_ASSET_CATEGORY_NOT_ALLOWED

    b13_category = D1_CATEGORY_TO_B13_ASSET_CATEGORY.get(category_code)
    if allowed_asset_categories and b13_category not in allowed_asset_categories:
        return False, BLOCK_ASSET_CATEGORY_NOT_ALLOWED

    asset_tier = str(asset.get("visibility_tier") or "reference")
    required = D1_ASSET_TIER_MIN_VISIBILITY.get(asset_tier, VISIBILITY_SOFT)
    if not _visibility_at_least(visibility_level, required):
        return False, BLOCK_ASSET_TIER_NOT_ALLOWED

    return True, None


def _collection_calendar_status(
    collection: dict[str, Any],
    calendar_consumer_policy: dict[str, Any],
) -> tuple[str, str | None]:
    collection_type = collection.get("collection_type")
    if collection_type == COLLECTION_TYPE_RHYTHM:
        if not calendar_consumer_policy.get("rhythm_pattern_visibility_allowed"):
            return "redacted", BLOCK_RHYTHM_VISIBILITY_NOT_ALLOWED
    if collection_type == COLLECTION_TYPE_CYCLE:
        if not calendar_consumer_policy.get("cycle_overlay_visibility_allowed"):
            return "redacted", BLOCK_CYCLE_VISIBILITY_NOT_ALLOWED
    return "visible", None


def _load_asset_registry(asset_registry: dict[str, Any] | None) -> dict[str, Any]:
    if asset_registry is not None:
        return asset_registry
    from todayflow_backend.data.symbolic_asset_definition_registry_loader import (
        load_symbolic_asset_definition_registry_v1,
    )

    return load_symbolic_asset_definition_registry_v1()


def _load_collection_registry(collection_registry: dict[str, Any] | None) -> dict[str, Any]:
    if collection_registry is not None:
        return collection_registry
    from todayflow_backend.data.symbolic_collection_registry_loader import (
        load_symbolic_collection_registry_v1,
    )

    return load_symbolic_collection_registry_v1()


def _idle_policy(
    *,
    blocked_reason: str,
    asset_registry: dict[str, Any] | None = None,
    collection_registry: dict[str, Any] | None = None,
    policy_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    return _build_policy_payload(
        visibility_level=VISIBILITY_NONE,
        asset_registry=_load_asset_registry(asset_registry),
        collection_registry=_load_collection_registry(collection_registry),
        allowed_asset_categories=[],
        calendar_consumer_policy={},
        commerce_policy_id=None,
        calendar_policy_id=None,
        blocked_reasons=[blocked_reason],
        policy_id=policy_id,
        created_at=created_at,
    )


def _build_policy_payload(
    *,
    visibility_level: str,
    asset_registry: dict[str, Any],
    collection_registry: dict[str, Any],
    allowed_asset_categories: list[str],
    calendar_consumer_policy: dict[str, Any],
    commerce_policy_id: str | None,
    calendar_policy_id: str | None,
    blocked_reasons: list[str],
    policy_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    definitions = asset_registry.get("symbolic_asset_definitions") or {}
    collections = collection_registry.get("symbolic_collections") or {}

    visible_assets: list[str] = []
    blocked_assets: list[str] = []
    redacted_assets: list[str] = []
    asset_block_reasons: dict[str, str] = {}

    collections_allowed = _visibility_at_least(visibility_level, VISIBILITY_STANDARD)
    associations_metadata_allowed = _visibility_at_least(visibility_level, VISIBILITY_FULL)

    for asset_code, asset in definitions.items():
        if visibility_level == VISIBILITY_NONE:
            blocked_assets.append(asset_code)
            asset_block_reasons[asset_code] = BLOCK_VISIBILITY_NONE
            continue

        allowed, reason = _asset_allowed_by_commerce(
            asset,
            visibility_level=visibility_level,
            allowed_asset_categories=allowed_asset_categories,
        )
        if allowed:
            visible_assets.append(asset_code)
        else:
            blocked_assets.append(asset_code)
            if reason:
                asset_block_reasons[asset_code] = reason

    visible_collections: list[str] = []
    redacted_collections: list[str] = []
    blocked_collections: list[str] = []
    collection_block_reasons: dict[str, str] = {}
    allowed_collection_types: set[str] = set()

    for collection_code, collection in collections.items():
        collection_type = collection.get("collection_type")
        if not isinstance(collection_type, str):
            blocked_collections.append(collection_code)
            collection_block_reasons[collection_code] = BLOCK_COLLECTION_TYPE_NOT_VISIBLE
            continue

        if not collections_allowed:
            blocked_collections.append(collection_code)
            collection_block_reasons[collection_code] = BLOCK_ASSETS_ONLY_POLICY
            continue

        member_codes = collection.get("asset_codes") or []
        if any(code not in visible_assets for code in member_codes):
            blocked_collections.append(collection_code)
            collection_block_reasons[collection_code] = BLOCK_ASSET_TIER_NOT_ALLOWED
            continue

        calendar_status, calendar_reason = _collection_calendar_status(
            collection,
            calendar_consumer_policy,
        )
        if calendar_status == "redacted":
            redacted_collections.append(collection_code)
            if calendar_reason:
                collection_block_reasons[collection_code] = calendar_reason
            continue

        visible_collections.append(collection_code)
        allowed_collection_types.add(collection_type)

    allowed_categories = sorted(
        {
            D1_CATEGORY_TO_B13_ASSET_CATEGORY[definitions[code]["category_code"]]
            for code in visible_assets
            if code in definitions
            and definitions[code].get("category_code") in D1_CATEGORY_TO_B13_ASSET_CATEGORY
        }
    )

    merged_blocked_reasons = list(dict.fromkeys(blocked_reasons + list(set(asset_block_reasons.values())) + list(set(collection_block_reasons.values()))))

    policy = {
        "contract_version": SYMBOLIC_VISIBILITY_POLICY_V1_CONTRACT,
        "policy_id": policy_id or generate_symbolic_visibility_policy_id(),
        "source_commerce_policy_id": commerce_policy_id,
        "source_calendar_consumer_policy_id": calendar_policy_id,
        "visibility_level": visibility_level,
        "visible_assets": sorted(visible_assets),
        "visible_collections": sorted(visible_collections),
        "redacted_assets": sorted(redacted_assets),
        "redacted_collections": sorted(redacted_collections),
        "blocked_assets": sorted(blocked_assets),
        "blocked_collections": sorted(blocked_collections),
        "allowed_categories": allowed_categories,
        "allowed_collection_types": sorted(allowed_collection_types),
        "associations_metadata_allowed": associations_metadata_allowed,
        "blocked_reasons": merged_blocked_reasons,
        "recommendation_allowed": False,
        "commerce_activation_allowed": False,
        "personalization_allowed": False,
        "created_at": created_at or _utc_now_iso(),
        "version": SYMBOLIC_VISIBILITY_POLICY_V1_VERSION,
    }

    errors = validate_symbolic_visibility_policy_v1(policy)
    if errors:
        raise SymbolicVisibilityPolicyError("; ".join(errors))

    return policy


def build_symbolic_visibility_policy_v1(
    commerce_policy: dict[str, Any] | None = None,
    *,
    calendar_consumer_policy: dict[str, Any] | None = None,
    asset_registry: dict[str, Any] | None = None,
    collection_registry: dict[str, Any] | None = None,
    policy_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """
    Build read-only symbolic visibility policy from B1.13 + E1.7 over D1.1/D1.3 registries.

    Visibility ≠ recommendation. No purchase prompts, targeting, or personalization.
    """
    if commerce_policy is None:
        return _idle_policy(
            blocked_reason=BLOCK_INVALID_COMMERCE_POLICY,
            policy_id=policy_id,
            created_at=created_at,
        )

    if commerce_policy.get("contract_version") != EVOLUTION_COMMERCE_VISIBILITY_POLICY_V1_CONTRACT:
        return _idle_policy(
            blocked_reason=BLOCK_INVALID_COMMERCE_POLICY,
            policy_id=policy_id,
            created_at=created_at,
        )

    commerce_errors = validate_evolution_commerce_visibility_policy_v1(commerce_policy)
    if commerce_errors:
        return _idle_policy(
            blocked_reason=BLOCK_INVALID_COMMERCE_POLICY,
            policy_id=policy_id,
            created_at=created_at,
        )

    calendar_policy = calendar_consumer_policy or {}
    if calendar_consumer_policy is not None:
        if calendar_consumer_policy.get("contract_version") != CALENDAR_INTELLIGENCE_CONSUMER_POLICY_V1_CONTRACT:
            return _idle_policy(
                blocked_reason=BLOCK_INVALID_CALENDAR_POLICY,
                policy_id=policy_id,
                created_at=created_at,
            )
        calendar_errors = validate_calendar_intelligence_consumer_policy_v1(calendar_consumer_policy)
        if calendar_errors:
            return _idle_policy(
                blocked_reason=BLOCK_INVALID_CALENDAR_POLICY,
                policy_id=policy_id,
                created_at=created_at,
            )
    else:
        calendar_policy = {
            "rhythm_pattern_visibility_allowed": True,
            "cycle_overlay_visibility_allowed": True,
        }

    if asset_registry is None:
        asset_registry = _load_asset_registry(None)

    if collection_registry is None:
        collection_registry = _load_collection_registry(None)

    visibility_level = _normalize_commerce_level(commerce_policy)
    allowed_asset_categories = list(commerce_policy.get("allowed_asset_categories") or [])

    blocked_reasons: list[str] = []
    if visibility_level == VISIBILITY_NONE:
        blocked_reasons.append(BLOCK_VISIBILITY_NONE)

    return _build_policy_payload(
        visibility_level=visibility_level,
        asset_registry=asset_registry,
        collection_registry=collection_registry,
        allowed_asset_categories=allowed_asset_categories,
        calendar_consumer_policy=calendar_policy,
        commerce_policy_id=commerce_policy.get("policy_id"),
        calendar_policy_id=calendar_consumer_policy.get("policy_id") if calendar_consumer_policy else None,
        blocked_reasons=blocked_reasons,
        policy_id=policy_id,
        created_at=created_at,
    )


def validate_symbolic_visibility_policy_v1(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if policy.get("contract_version") != SYMBOLIC_VISIBILITY_POLICY_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in SYMBOLIC_VISIBILITY_POLICY_V1_KEYS:
        if key not in policy:
            errors.append(f"missing field: {key}")

    forbidden = set(policy.keys()) & FORBIDDEN_SYMBOLIC_VISIBILITY_FIELDS
    if forbidden:
        errors.append(f"forbidden fields: {sorted(forbidden)}")

    level = policy.get("visibility_level")
    if level not in VISIBILITY_ORDER:
        errors.append("invalid visibility_level")

    if policy.get("recommendation_allowed") is not False:
        errors.append("recommendation_allowed must be false")
    if policy.get("commerce_activation_allowed") is not False:
        errors.append("commerce_activation_allowed must be false")
    if policy.get("personalization_allowed") is not False:
        errors.append("personalization_allowed must be false")

    if not isinstance(policy.get("associations_metadata_allowed"), bool):
        errors.append("associations_metadata_allowed must be boolean")

    list_fields = (
        "visible_assets",
        "visible_collections",
        "redacted_assets",
        "redacted_collections",
        "blocked_assets",
        "blocked_collections",
        "allowed_categories",
        "allowed_collection_types",
        "blocked_reasons",
    )
    for field in list_fields:
        if not isinstance(policy.get(field), list):
            errors.append(f"{field} must be array")

    if level == VISIBILITY_NONE:
        if policy.get("visible_assets") or policy.get("visible_collections"):
            errors.append("visibility none requires empty visible_assets and visible_collections")
        if policy.get("associations_metadata_allowed") is not False:
            errors.append("visibility none requires associations_metadata_allowed false")

    if level == VISIBILITY_SOFT:
        if policy.get("visible_collections"):
            errors.append("soft visibility requires empty visible_collections")
        if policy.get("associations_metadata_allowed") is not False:
            errors.append("soft visibility requires associations_metadata_allowed false")

    if level == VISIBILITY_STANDARD and policy.get("associations_metadata_allowed") is not False:
        errors.append("standard visibility requires associations_metadata_allowed false")

    if level == VISIBILITY_FULL and policy.get("associations_metadata_allowed") is not True:
        errors.append("full visibility requires associations_metadata_allowed true")

    return errors
