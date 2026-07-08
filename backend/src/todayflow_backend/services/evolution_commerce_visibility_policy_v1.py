"""B1.13 — Evolution → Commerce visibility policy (B1.7 commerce_visibility slice as cap)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.evolution_effect_consumer_map_v1 import (
    CONSUMER_COMMERCE_VISIBILITY,
    EVOLUTION_EFFECT_CONSUMER_SLICE_V1_CONTRACT,
    validate_evolution_effect_consumer_slice_v1,
)
from todayflow_backend.services.evolution_effect_runtime_policy_v1 import (
    EVOLUTION_EFFECT_RUNTIME_POLICY_V1_CONTRACT,
)

EVOLUTION_COMMERCE_VISIBILITY_POLICY_V1_VERSION = "1.0.0"

EVOLUTION_COMMERCE_VISIBILITY_POLICY_V1_CONTRACT = "evolution_commerce_visibility_policy_v1"

VISIBILITY_NONE = "none"
VISIBILITY_SOFT = "soft"
VISIBILITY_STANDARD = "standard"
VISIBILITY_FULL = "full"

SURFACE_SHOP_ENTRY = "shop_entry"
SURFACE_SYMBOLIC_ASSETS = "symbolic_assets"
SURFACE_THEMED_COLLECTIONS = "themed_collections"
SURFACE_BUNDLES = "bundles"

ASSET_STONES = "stones"
ASSET_CANDLES = "candles"
ASSET_JOURNALS = "journals"
ASSET_CARDS = "cards"
ASSET_SYMBOLIC_SETS = "symbolic_sets"

VISIBILITY_ORDER = {
    VISIBILITY_NONE: 0,
    VISIBILITY_SOFT: 1,
    VISIBILITY_STANDARD: 2,
    VISIBILITY_FULL: 3,
}

REGISTRY_VISIBILITY_TO_POLICY = {
    "none": VISIBILITY_NONE,
    "soft": VISIBILITY_SOFT,
    "full": VISIBILITY_FULL,
}

SYMBOLIC_TIER_ASSET_CATEGORIES: dict[str, list[str]] = {
    "none": [],
    "soft": [ASSET_STONES, ASSET_CANDLES],
    "themed": [ASSET_STONES, ASSET_CANDLES, ASSET_JOURNALS, ASSET_CARDS],
    "full": [ASSET_STONES, ASSET_CANDLES, ASSET_JOURNALS, ASSET_CARDS, ASSET_SYMBOLIC_SETS],
}

VISIBILITY_ALLOWED_SURFACES: dict[str, list[str]] = {
    VISIBILITY_NONE: [],
    VISIBILITY_SOFT: [SURFACE_SHOP_ENTRY],
    VISIBILITY_STANDARD: [SURFACE_SHOP_ENTRY, SURFACE_SYMBOLIC_ASSETS, SURFACE_THEMED_COLLECTIONS],
    VISIBILITY_FULL: [
        SURFACE_SHOP_ENTRY,
        SURFACE_SYMBOLIC_ASSETS,
        SURFACE_THEMED_COLLECTIONS,
        SURFACE_BUNDLES,
    ],
}

BLOCK_COMMERCE_NOT_READY = "commerce_not_ready"
BLOCK_STAGE_VISIBILITY_NONE = "stage_visibility_none"
BLOCK_TARGETING_FORBIDDEN = "targeting_forbidden"
BLOCK_PURCHASE_RECOMMENDATION_FORBIDDEN = "purchase_recommendation_forbidden"
BLOCK_PERSONALIZED_OFFER_FORBIDDEN = "personalized_offer_forbidden"
BLOCK_INVALID_EVOLUTION_SLICE = "invalid_evolution_slice"
BLOCK_FULL_POLICY_PASSED = "full_policy_passed"

COMMERCE_READINESS_KEY = "commerce_visibility"

STAGE_COMMERCE_PROFILES: dict[str, dict[str, Any]] = {
    "seeker": {"commerce_visibility_level": VISIBILITY_NONE},
    "observer": {"commerce_visibility_level": VISIBILITY_SOFT},
    "practitioner": {"commerce_visibility_level": VISIBILITY_STANDARD},
    "explorer": {"commerce_visibility_level": VISIBILITY_STANDARD},
    "architect": {"commerce_visibility_level": VISIBILITY_FULL},
    "mentor": {"commerce_visibility_level": VISIBILITY_FULL},
    "master": {"commerce_visibility_level": VISIBILITY_FULL},
}

EVOLUTION_COMMERCE_VISIBILITY_POLICY_V1_KEYS = frozenset(
    {
        "contract_version",
        "policy_id",
        "source_evolution_slice_id",
        "evolution_stage",
        "commerce_visibility_level",
        "allowed_surfaces",
        "blocked_surfaces",
        "allowed_asset_categories",
        "targeting_allowed",
        "purchase_recommendation_allowed",
        "personalized_offer_allowed",
        "commerce_mutation_allowed",
        "profile_update_allowed",
        "memory_update_allowed",
        "created_at",
    }
)

FORBIDDEN_COMMERCE_POLICY_FIELDS = frozenset(
    {
        "sku",
        "product_id",
        "product",
        "products",
        "recommended_product",
        "recommended_sku",
        "purchase_prompt",
        "checkout",
        "recommendation",
        "targeting",
        "personalized_offer",
        "sales_copy",
        "llm_call",
        "insight",
        "score",
        "stage_update",
    }
)

ALL_SURFACES = (
    SURFACE_SHOP_ENTRY,
    SURFACE_SYMBOLIC_ASSETS,
    SURFACE_THEMED_COLLECTIONS,
    SURFACE_BUNDLES,
)


class EvolutionCommerceVisibilityPolicyError(ValueError):
    """Raised when commerce visibility policy inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_commerce_visibility_policy_id() -> str:
    return f"ecvp-{uuid4()}"


def _is_valid_commerce_slice(evolution_slice: dict[str, Any]) -> tuple[bool, str | None]:
    if evolution_slice.get("contract_version") == EVOLUTION_EFFECT_RUNTIME_POLICY_V1_CONTRACT:
        return False, BLOCK_FULL_POLICY_PASSED
    if evolution_slice.get("contract_version") != EVOLUTION_EFFECT_CONSUMER_SLICE_V1_CONTRACT:
        return False, BLOCK_INVALID_EVOLUTION_SLICE
    if evolution_slice.get("consumer_id") != CONSUMER_COMMERCE_VISIBILITY:
        return False, BLOCK_INVALID_EVOLUTION_SLICE
    errors = validate_evolution_effect_consumer_slice_v1(
        evolution_slice,
        consumer_id=CONSUMER_COMMERCE_VISIBILITY,
    )
    if errors:
        return False, BLOCK_INVALID_EVOLUTION_SLICE
    return True, None


def _normalize_registry_visibility(raw: str | None) -> str:
    if raw is None:
        return VISIBILITY_NONE
    return REGISTRY_VISIBILITY_TO_POLICY.get(str(raw), VISIBILITY_NONE)


def _slice_commerce_visibility(evolution_slice: dict[str, Any]) -> str:
    limits = evolution_slice.get("effect_limits") or {}
    commerce = (evolution_slice.get("allowed_effects") or {}).get("commerce_effects") or {}
    raw = limits.get("commerce_visibility")
    if raw is None:
        raw = commerce.get("commerce_visibility")
    if not commerce and raw not in (None, VISIBILITY_NONE, "none"):
        return VISIBILITY_NONE
    return _normalize_registry_visibility(str(raw) if raw is not None else None)


def _slice_symbolic_asset_tier(evolution_slice: dict[str, Any]) -> str:
    limits = evolution_slice.get("effect_limits") or {}
    commerce = (evolution_slice.get("allowed_effects") or {}).get("commerce_effects") or {}
    tier = limits.get("symbolic_asset_tier")
    if tier is None:
        tier = commerce.get("symbolic_asset_tier")
    if tier is None:
        return "none"
    return str(tier)


def _min_visibility(stage_level: str, slice_level: str) -> tuple[str, bool]:
    stage_level = stage_level if stage_level in VISIBILITY_ORDER else VISIBILITY_NONE
    slice_level = slice_level if slice_level in VISIBILITY_ORDER else VISIBILITY_NONE
    if VISIBILITY_ORDER[slice_level] < VISIBILITY_ORDER[stage_level]:
        return slice_level, True
    return stage_level, False


def _commerce_system_ready(commerce_readiness: dict[str, bool] | None) -> bool:
    if commerce_readiness is None:
        return True
    return bool(commerce_readiness.get(COMMERCE_READINESS_KEY, False))


def _blocked_surface_entries(
    allowed_surfaces: list[str],
    reasons: dict[str, str],
) -> list[dict[str, str]]:
    allowed = set(allowed_surfaces)
    blocked: list[dict[str, str]] = []
    for surface in ALL_SURFACES:
        if surface not in allowed:
            blocked.append({"surface": surface, "reason": reasons.get(surface, BLOCK_STAGE_VISIBILITY_NONE)})
    return blocked


def _idle_policy(
    *,
    blocked_reason: str,
    policy_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    blocked_surfaces = _blocked_surface_entries(
        [],
        {surface: blocked_reason for surface in ALL_SURFACES},
    )
    return {
        "contract_version": EVOLUTION_COMMERCE_VISIBILITY_POLICY_V1_CONTRACT,
        "policy_id": policy_id or generate_commerce_visibility_policy_id(),
        "source_evolution_slice_id": None,
        "evolution_stage": None,
        "commerce_visibility_level": VISIBILITY_NONE,
        "allowed_surfaces": [],
        "blocked_surfaces": blocked_surfaces,
        "allowed_asset_categories": [],
        "targeting_allowed": False,
        "purchase_recommendation_allowed": False,
        "personalized_offer_allowed": False,
        "commerce_mutation_allowed": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "created_at": created_at or _utc_now_iso(),
    }


def build_evolution_commerce_visibility_policy_v1(
    evolution_slice: dict[str, Any] | None = None,
    *,
    evolution_user_state: dict[str, Any] | None = None,
    commerce_readiness: dict[str, bool] | None = None,
    policy_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """
    Build read-only commerce visibility policy from a B1.7 commerce_visibility slice.

    Commerce visibility ≠ commerce recommendation. No SKU selection or targeting.
    """
    if evolution_slice is None:
        return _idle_policy(
            blocked_reason=BLOCK_INVALID_EVOLUTION_SLICE,
            policy_id=policy_id,
            created_at=created_at,
        )

    valid, invalid_reason = _is_valid_commerce_slice(evolution_slice)
    if not valid:
        return _idle_policy(
            blocked_reason=invalid_reason or BLOCK_INVALID_EVOLUTION_SLICE,
            policy_id=policy_id,
            created_at=created_at,
        )

    stage = str(evolution_slice.get("current_stage") or "seeker")
    if evolution_user_state is not None:
        stage = str(evolution_user_state.get("current_stage") or stage)

    profile = STAGE_COMMERCE_PROFILES.get(stage, STAGE_COMMERCE_PROFILES["seeker"])
    slice_level = _slice_commerce_visibility(evolution_slice)
    symbolic_tier = _slice_symbolic_asset_tier(evolution_slice)

    visibility_level, slice_capped = _min_visibility(
        profile["commerce_visibility_level"],
        slice_level,
    )

    blocked_reasons: dict[str, str] = {}
    if slice_capped:
        for surface in ALL_SURFACES:
            blocked_reasons[surface] = BLOCK_STAGE_VISIBILITY_NONE

    if visibility_level == VISIBILITY_NONE:
        for surface in ALL_SURFACES:
            blocked_reasons.setdefault(surface, BLOCK_STAGE_VISIBILITY_NONE)

    allowed_surfaces = list(VISIBILITY_ALLOWED_SURFACES.get(visibility_level, []))
    allowed_asset_categories = list(SYMBOLIC_TIER_ASSET_CATEGORIES.get(symbolic_tier, []))

    if visibility_level == VISIBILITY_NONE:
        allowed_asset_categories = []
    elif visibility_level == VISIBILITY_SOFT:
        allowed_asset_categories = [
            category
            for category in allowed_asset_categories
            if category in {ASSET_STONES, ASSET_CANDLES}
        ]

    if not _commerce_system_ready(commerce_readiness):
        visibility_level = VISIBILITY_NONE
        allowed_surfaces = []
        allowed_asset_categories = []
        for surface in ALL_SURFACES:
            blocked_reasons[surface] = BLOCK_COMMERCE_NOT_READY

    blocked_surfaces = _blocked_surface_entries(allowed_surfaces, blocked_reasons)

    policy = {
        "contract_version": EVOLUTION_COMMERCE_VISIBILITY_POLICY_V1_CONTRACT,
        "policy_id": policy_id or generate_commerce_visibility_policy_id(),
        "source_evolution_slice_id": evolution_slice.get("slice_id"),
        "evolution_stage": stage,
        "commerce_visibility_level": visibility_level,
        "allowed_surfaces": allowed_surfaces,
        "blocked_surfaces": blocked_surfaces,
        "allowed_asset_categories": allowed_asset_categories,
        "targeting_allowed": False,
        "purchase_recommendation_allowed": False,
        "personalized_offer_allowed": False,
        "commerce_mutation_allowed": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "created_at": created_at or _utc_now_iso(),
    }

    errors = validate_evolution_commerce_visibility_policy_v1(policy)
    if errors:
        raise EvolutionCommerceVisibilityPolicyError("; ".join(errors))

    return policy


def validate_evolution_commerce_visibility_policy_v1(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if policy.get("contract_version") != EVOLUTION_COMMERCE_VISIBILITY_POLICY_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in EVOLUTION_COMMERCE_VISIBILITY_POLICY_V1_KEYS:
        if key not in policy:
            errors.append(f"missing field: {key}")

    forbidden = set(policy.keys()) & FORBIDDEN_COMMERCE_POLICY_FIELDS
    if forbidden:
        errors.append(f"forbidden policy fields: {sorted(forbidden)}")

    level = policy.get("commerce_visibility_level")
    if level not in VISIBILITY_ORDER:
        errors.append("invalid commerce_visibility_level")

    if policy.get("targeting_allowed") is not False:
        errors.append("targeting_allowed must be false")
    if policy.get("purchase_recommendation_allowed") is not False:
        errors.append("purchase_recommendation_allowed must be false")
    if policy.get("personalized_offer_allowed") is not False:
        errors.append("personalized_offer_allowed must be false")
    if policy.get("commerce_mutation_allowed") is not False:
        errors.append("commerce_mutation_allowed must be false")
    if policy.get("profile_update_allowed") is not False:
        errors.append("profile_update_allowed must be false")
    if policy.get("memory_update_allowed") is not False:
        errors.append("memory_update_allowed must be false")

    if not isinstance(policy.get("allowed_surfaces"), list):
        errors.append("allowed_surfaces must be array")
    if not isinstance(policy.get("blocked_surfaces"), list):
        errors.append("blocked_surfaces must be array")
    if not isinstance(policy.get("allowed_asset_categories"), list):
        errors.append("allowed_asset_categories must be array")

    for surface in policy.get("allowed_surfaces") or []:
        if surface not in ALL_SURFACES:
            errors.append(f"invalid allowed_surface: {surface}")

    for entry in policy.get("blocked_surfaces") or []:
        if not isinstance(entry, dict):
            errors.append("blocked_surfaces entries must be objects")
            continue
        if "surface" not in entry or "reason" not in entry:
            errors.append("blocked_surfaces entry must include surface and reason")

    return errors
