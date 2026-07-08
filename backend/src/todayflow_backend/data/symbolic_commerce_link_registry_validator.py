"""D1.5 — Validate Symbolic Commerce Link registry (refs only, no symbolic definitions)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

SYMBOLIC_COMMERCE_LINK_REGISTRY_V1_CONTRACT = "symbolic_commerce_link_registry_v1"

SYMBOLIC_COMMERCE_LINK_V1_CONTRACT = "symbolic_commerce_link_v1"

ALLOWED_REGISTRY_STATUSES = frozenset({"draft", "active"})

ALLOWED_LINK_STATUSES = frozenset({"draft", "active"})

ALLOWED_LINK_MODES = frozenset({"references"})

ALLOWED_COMMERCE_PRODUCT_TYPES = frozenset(
    {
        "physical_stone",
        "ritual_candle",
        "tarot_deck",
        "journal",
        "bracelet",
        "digital_deck",
        "practice_kit",
        "gift_set",
    }
)

LINK_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

SKU_REF_PATTERN = re.compile(r"^[a-z][a-z0-9_.-]*$")

FORBIDDEN_TEXT_PATTERN = re.compile(
    r"(recommend|needed_for|fixes|heals|diagnos|medical|financial|"
    r"psychological|personalized|targeting|offer_context|you_should|"
    r"must_buy|shop_now)",
    re.I,
)

FORBIDDEN_LINK_FIELDS = frozenset(
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
        "user_id",
        "collection_code",
        "collection_type",
        "title",
        "description",
        "sales_copy",
        "ui_copy",
        "marketing_copy",
        "needed_for",
        "fixes",
        "heals",
        "price",
        "pricing",
        "inventory",
        "stock",
        "checkout",
        "purchase_prompt",
        "bundle_pricing",
        "product_bundle",
    }
)

SYMBOLIC_COMMERCE_LINK_V1_KEYS = frozenset(
    {
        "contract_version",
        "link_id",
        "sku_ref",
        "asset_code",
        "product_type",
        "link_mode",
        "status",
        "version",
        "created_at",
    }
)

SYMBOLIC_COMMERCE_LINK_REGISTRY_V1_TOP_KEYS = frozenset(
    {
        "contract_version",
        "domain",
        "version",
        "status",
        "description",
        "symbolic_commerce_links",
    }
)

MIN_CANONICAL_LINK_COUNT = 10
MAX_CANONICAL_LINK_COUNT = 50


@dataclass(frozen=True)
class SymbolicCommerceLinkValidationContext:
    asset_codes: frozenset[str]


class SymbolicCommerceLinkRegistryValidationError(Exception):
    """Raised when symbolic commerce link registry payload fails validation."""


def validate_symbolic_commerce_link_v1(
    link: dict[str, Any],
    *,
    context: SymbolicCommerceLinkValidationContext,
    prefix: str = "",
) -> list[str]:
    errors: list[str] = []
    label = prefix or "symbolic_commerce_link"

    if link.get("contract_version") != SYMBOLIC_COMMERCE_LINK_V1_CONTRACT:
        errors.append(f"{label}: invalid contract_version")

    for key in SYMBOLIC_COMMERCE_LINK_V1_KEYS:
        if key not in link:
            errors.append(f"{label}: missing field {key!r}")

    forbidden = set(link.keys()) & FORBIDDEN_LINK_FIELDS
    if forbidden:
        errors.append(f"{label}: forbidden symbolic/commerce-mutation fields: {sorted(forbidden)}")

    link_id = link.get("link_id")
    if not isinstance(link_id, str) or not link_id:
        errors.append(f"{label}: link_id required")
    elif not LINK_ID_PATTERN.match(link_id):
        errors.append(f"{label}: link_id must be snake_case")

    sku_ref = link.get("sku_ref")
    if not isinstance(sku_ref, str) or not sku_ref:
        errors.append(f"{label}: sku_ref required")
    elif not SKU_REF_PATTERN.match(sku_ref):
        errors.append(f"{label}: sku_ref must be lowercase machine ref")

    asset_code = link.get("asset_code")
    if not isinstance(asset_code, str) or not asset_code:
        errors.append(f"{label}: asset_code required")
    elif asset_code not in context.asset_codes:
        errors.append(f"{label}: asset_code {asset_code!r} not in D1.1 registry")

    if link.get("product_type") not in ALLOWED_COMMERCE_PRODUCT_TYPES:
        errors.append(f"{label}: invalid product_type")

    if link.get("link_mode") not in ALLOWED_LINK_MODES:
        errors.append(f"{label}: link_mode must be references")

    if link.get("status") not in ALLOWED_LINK_STATUSES:
        errors.append(f"{label}: invalid status")

    version = link.get("version")
    if not isinstance(version, str) or not version.strip():
        errors.append(f"{label}: version required")

    created_at = link.get("created_at")
    if not isinstance(created_at, str) or len(created_at) < 10:
        errors.append(f"{label}: created_at must be ISO timestamp string")

    for text_field in ("link_id", "sku_ref", "asset_code"):
        value = link.get(text_field)
        if isinstance(value, str) and FORBIDDEN_TEXT_PATTERN.search(value):
            errors.append(f"{label}: {text_field} contains forbidden language")

    return errors


def validate_symbolic_commerce_link_registry_v1(
    payload: dict[str, Any],
    *,
    context: SymbolicCommerceLinkValidationContext,
) -> list[str]:
    errors: list[str] = []

    if payload.get("contract_version") != SYMBOLIC_COMMERCE_LINK_REGISTRY_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in SYMBOLIC_COMMERCE_LINK_REGISTRY_V1_TOP_KEYS:
        if key not in payload:
            errors.append(f"missing top-level field: {key}")

    if payload.get("domain") != "symbolic_commerce":
        errors.append("domain must be symbolic_commerce")

    if payload.get("status") not in ALLOWED_REGISTRY_STATUSES:
        errors.append("invalid top-level status")

    links = payload.get("symbolic_commerce_links")
    if not isinstance(links, dict):
        errors.append("symbolic_commerce_links must be object")
        return errors

    count = len(links)
    if count < MIN_CANONICAL_LINK_COUNT:
        errors.append(f"symbolic_commerce_links must include >= {MIN_CANONICAL_LINK_COUNT} links")
    if count > MAX_CANONICAL_LINK_COUNT:
        errors.append(f"symbolic_commerce_links must include <= {MAX_CANONICAL_LINK_COUNT} links")

    seen_ids: set[str] = set()
    seen_skus: set[str] = set()
    for link_id, entry in links.items():
        prefix = f"symbolic_commerce_link[{link_id}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: must be object")
            continue

        if link_id in seen_ids:
            errors.append(f"duplicate link_id key: {link_id!r}")
        seen_ids.add(link_id)

        entry_errors = validate_symbolic_commerce_link_v1(entry, context=context, prefix=prefix)
        errors.extend(entry_errors)

        if entry.get("link_id") != link_id:
            errors.append(f"{prefix}: link_id must match registry key")

        sku_ref = entry.get("sku_ref")
        if isinstance(sku_ref, str):
            if sku_ref in seen_skus:
                errors.append(f"duplicate sku_ref: {sku_ref!r}")
            seen_skus.add(sku_ref)

    return errors
