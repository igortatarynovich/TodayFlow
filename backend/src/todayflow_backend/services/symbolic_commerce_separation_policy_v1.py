"""D1.5 — Symbolic commerce separation policy (commerce refs symbolic; never defines it)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.data.symbolic_commerce_link_registry_validator import (
    SYMBOLIC_COMMERCE_LINK_REGISTRY_V1_CONTRACT,
    SymbolicCommerceLinkValidationContext,
    validate_symbolic_commerce_link_registry_v1,
)
from todayflow_backend.services.symbolic_visibility_policy_v1 import (
    SYMBOLIC_VISIBILITY_POLICY_V1_CONTRACT,
    validate_symbolic_visibility_policy_v1,
)

SYMBOLIC_COMMERCE_SEPARATION_POLICY_V1_VERSION = "1.0.0"
SYMBOLIC_COMMERCE_SEPARATION_POLICY_V1_CONTRACT = "symbolic_commerce_separation_policy_v1"

BLOCK_INVALID_LINK_REGISTRY = "invalid_link_registry"
BLOCK_INVALID_VISIBILITY_POLICY = "invalid_visibility_policy"
BLOCK_COMMERCE_DEFINES_SYMBOLIC = "commerce_defines_symbolic_layer"
BLOCK_UNKNOWN_ASSET_REF = "unknown_asset_ref"
BLOCK_UNKNOWN_SKU_REF = "unknown_sku_ref"

SYMBOLIC_LAYER_SOURCE_CONTRACTS = (
    "symbolic_asset_definition_v1",
    "symbolic_asset_association_v1",
    "symbolic_collection_v1",
    "symbolic_visibility_policy_v1",
)

ALLOWED_COMMERCE_PRODUCT_REF_FIELDS = frozenset(
    {
        "sku_ref",
        "asset_code",
        "symbolic_asset_ref",
        "product_type",
        "link_id",
    }
)

FORBIDDEN_COMMERCE_PRODUCT_SYMBOLIC_FIELDS = frozenset(
    {
        "asset_name",
        "asset_category",
        "category_code",
        "theme_codes",
        "primary_theme_codes",
        "association_refs",
        "associations",
        "association_type",
        "target_ref",
        "compatible_contexts",
        "collection_code",
        "collection_type",
        "meaning",
        "meanings",
        "interpretation",
        "interpretations",
        "recommendation",
        "recommendation_id",
        "recommendations",
        "visibility_tier",
        "visibility_level",
        "offer_context",
        "targeting",
        "personalization",
        "personalized",
        "needed_for",
        "fixes",
        "heals",
        "sales_copy",
        "ui_copy",
        "marketing_copy",
    }
)

SYMBOLIC_COMMERCE_SEPARATION_POLICY_V1_KEYS = frozenset(
    {
        "contract_version",
        "policy_id",
        "separation_enforced",
        "commerce_may_reference_assets",
        "commerce_may_define_assets",
        "visibility_owned_by_symbolic_layer",
        "recommendation_from_commerce_allowed",
        "validated_links",
        "rejected_product_fields",
        "product_separation_valid",
        "blocked_reasons",
        "symbolic_layer_source_contracts",
        "source_link_registry_version",
        "source_visibility_policy_id",
        "created_at",
        "version",
    }
)

FORBIDDEN_SEPARATION_POLICY_FIELDS = frozenset(
    {
        "sku",
        "price",
        "pricing",
        "inventory",
        "checkout",
        "purchase_prompt",
        "offer",
        "targeting_rules",
        "recommendation",
        "ranking",
    }
)


class SymbolicCommerceSeparationPolicyError(ValueError):
    """Raised when separation policy inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_symbolic_commerce_separation_policy_id() -> str:
    return f"scsp-{uuid4()}"


def validate_commerce_product_separation_v1(product: dict[str, Any]) -> list[str]:
    """Reject commerce payloads that attempt to define the symbolic layer."""
    errors: list[str] = []

    if not isinstance(product, dict):
        return ["commerce_product must be object"]

    forbidden = sorted(set(product.keys()) & FORBIDDEN_COMMERCE_PRODUCT_SYMBOLIC_FIELDS)
    if forbidden:
        errors.append(f"commerce product defines symbolic layer: {forbidden}")

    asset_code = product.get("asset_code") or product.get("symbolic_asset_ref")
    if asset_code is None and "sku_ref" not in product:
        errors.append("commerce product must include sku_ref and/or asset_code ref")

    return errors


def validate_symbolic_commerce_separation_policy_v1(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if policy.get("contract_version") != SYMBOLIC_COMMERCE_SEPARATION_POLICY_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in SYMBOLIC_COMMERCE_SEPARATION_POLICY_V1_KEYS:
        if key not in policy:
            errors.append(f"missing field: {key}")

    forbidden = set(policy.keys()) & FORBIDDEN_SEPARATION_POLICY_FIELDS
    if forbidden:
        errors.append(f"forbidden fields: {sorted(forbidden)}")

    if policy.get("separation_enforced") is not True:
        errors.append("separation_enforced must be true")
    if policy.get("commerce_may_reference_assets") is not True:
        errors.append("commerce_may_reference_assets must be true")
    if policy.get("commerce_may_define_assets") is not False:
        errors.append("commerce_may_define_assets must be false")
    if policy.get("visibility_owned_by_symbolic_layer") is not True:
        errors.append("visibility_owned_by_symbolic_layer must be true")
    if policy.get("recommendation_from_commerce_allowed") is not False:
        errors.append("recommendation_from_commerce_allowed must be false")

    if not isinstance(policy.get("validated_links"), list):
        errors.append("validated_links must be array")
    if not isinstance(policy.get("rejected_product_fields"), list):
        errors.append("rejected_product_fields must be array")
    if not isinstance(policy.get("blocked_reasons"), list):
        errors.append("blocked_reasons must be array")
    if not isinstance(policy.get("product_separation_valid"), bool):
        errors.append("product_separation_valid must be boolean")

    contracts = policy.get("symbolic_layer_source_contracts")
    if not isinstance(contracts, list) or list(contracts) != list(SYMBOLIC_LAYER_SOURCE_CONTRACTS):
        errors.append("symbolic_layer_source_contracts must list D1.1–D1.4 contracts")

    return errors


def build_symbolic_commerce_separation_policy_v1(
    link_registry: dict[str, Any] | None = None,
    *,
    commerce_product: dict[str, Any] | None = None,
    symbolic_visibility_policy: dict[str, Any] | None = None,
    asset_codes: frozenset[str] | None = None,
    policy_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """
    Enforce Symbolic Layer ownership: commerce may reference asset_code/sku links only.

    Commerce cannot define meanings, associations, visibility, or recommendations.
    """
    blocked_reasons: list[str] = []
    validated_links: list[dict[str, str]] = []
    rejected_product_fields: list[str] = []
    product_separation_valid = True

    if link_registry is None:
        from todayflow_backend.data.symbolic_commerce_link_registry_loader import (
            load_symbolic_commerce_link_registry_v1,
        )
        from todayflow_backend.data.symbolic_asset_definition_registry_loader import (
            load_symbolic_asset_definition_registry_v1,
        )

        link_registry = load_symbolic_commerce_link_registry_v1()
        if asset_codes is None:
            definitions = load_symbolic_asset_definition_registry_v1().get(
                "symbolic_asset_definitions"
            ) or {}
            asset_codes = frozenset(definitions.keys())

    if asset_codes is None:
        asset_codes = frozenset()

    if link_registry.get("contract_version") != SYMBOLIC_COMMERCE_LINK_REGISTRY_V1_CONTRACT:
        return _idle_separation_policy(
            blocked_reason=BLOCK_INVALID_LINK_REGISTRY,
            policy_id=policy_id,
            created_at=created_at,
        )

    context = SymbolicCommerceLinkValidationContext(asset_codes=asset_codes)
    registry_errors = validate_symbolic_commerce_link_registry_v1(
        link_registry,
        context=context,
    )
    if registry_errors:
        return _idle_separation_policy(
            blocked_reason=BLOCK_INVALID_LINK_REGISTRY,
            policy_id=policy_id,
            created_at=created_at,
        )

    visibility_policy_id = None
    if symbolic_visibility_policy is not None:
        if symbolic_visibility_policy.get("contract_version") != SYMBOLIC_VISIBILITY_POLICY_V1_CONTRACT:
            return _idle_separation_policy(
                blocked_reason=BLOCK_INVALID_VISIBILITY_POLICY,
                policy_id=policy_id,
                created_at=created_at,
            )
        visibility_errors = validate_symbolic_visibility_policy_v1(symbolic_visibility_policy)
        if visibility_errors:
            return _idle_separation_policy(
                blocked_reason=BLOCK_INVALID_VISIBILITY_POLICY,
                policy_id=policy_id,
                created_at=created_at,
            )
        visibility_policy_id = symbolic_visibility_policy.get("policy_id")

    links = link_registry.get("symbolic_commerce_links") or {}
    for link_id, entry in links.items():
        if isinstance(entry, dict) and entry.get("status") == "active":
            validated_links.append(
                {
                    "link_id": link_id,
                    "sku_ref": str(entry.get("sku_ref") or ""),
                    "asset_code": str(entry.get("asset_code") or ""),
                }
            )

    if commerce_product is not None:
        product_errors = validate_commerce_product_separation_v1(commerce_product)
        if product_errors:
            product_separation_valid = False
            blocked_reasons.append(BLOCK_COMMERCE_DEFINES_SYMBOLIC)
            for err in product_errors:
                if err.startswith("commerce product defines symbolic layer:"):
                    rejected_product_fields.extend(
                        err.split(":", 1)[1].strip().strip("[]").replace("'", "").split(", ")
                    )

        asset_code = commerce_product.get("asset_code") or commerce_product.get("symbolic_asset_ref")
        if isinstance(asset_code, str) and asset_code not in asset_codes:
            product_separation_valid = False
            blocked_reasons.append(BLOCK_UNKNOWN_ASSET_REF)

        sku_ref = commerce_product.get("sku_ref")
        if isinstance(sku_ref, str):
            known_skus = {item["sku_ref"] for item in validated_links}
            if sku_ref not in known_skus:
                product_separation_valid = False
                blocked_reasons.append(BLOCK_UNKNOWN_SKU_REF)

    policy = {
        "contract_version": SYMBOLIC_COMMERCE_SEPARATION_POLICY_V1_CONTRACT,
        "policy_id": policy_id or generate_symbolic_commerce_separation_policy_id(),
        "separation_enforced": True,
        "commerce_may_reference_assets": True,
        "commerce_may_define_assets": False,
        "visibility_owned_by_symbolic_layer": True,
        "recommendation_from_commerce_allowed": False,
        "validated_links": validated_links,
        "rejected_product_fields": sorted(set(rejected_product_fields)),
        "product_separation_valid": product_separation_valid,
        "blocked_reasons": list(dict.fromkeys(blocked_reasons)),
        "symbolic_layer_source_contracts": list(SYMBOLIC_LAYER_SOURCE_CONTRACTS),
        "source_link_registry_version": link_registry.get("version"),
        "source_visibility_policy_id": visibility_policy_id,
        "created_at": created_at or _utc_now_iso(),
        "version": SYMBOLIC_COMMERCE_SEPARATION_POLICY_V1_VERSION,
    }

    errors = validate_symbolic_commerce_separation_policy_v1(policy)
    if errors:
        raise SymbolicCommerceSeparationPolicyError("; ".join(errors))

    return policy


def _idle_separation_policy(
    *,
    blocked_reason: str,
    policy_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    policy = {
        "contract_version": SYMBOLIC_COMMERCE_SEPARATION_POLICY_V1_CONTRACT,
        "policy_id": policy_id or generate_symbolic_commerce_separation_policy_id(),
        "separation_enforced": True,
        "commerce_may_reference_assets": True,
        "commerce_may_define_assets": False,
        "visibility_owned_by_symbolic_layer": True,
        "recommendation_from_commerce_allowed": False,
        "validated_links": [],
        "rejected_product_fields": [],
        "product_separation_valid": False,
        "blocked_reasons": [blocked_reason],
        "symbolic_layer_source_contracts": list(SYMBOLIC_LAYER_SOURCE_CONTRACTS),
        "source_link_registry_version": None,
        "source_visibility_policy_id": None,
        "created_at": created_at or _utc_now_iso(),
        "version": SYMBOLIC_COMMERCE_SEPARATION_POLICY_V1_VERSION,
    }
    errors = validate_symbolic_commerce_separation_policy_v1(policy)
    if errors:
        raise SymbolicCommerceSeparationPolicyError("; ".join(errors))
    return policy
