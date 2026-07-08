"""B1.6 — Evolution effect runtime policy (B1.5 registry → allowed runtime effects)."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.data.evolution_cd_loader import load_evolution_cd_v1
from todayflow_backend.data.evolution_cd_validator import CANONICAL_STAGE_ORDER
from todayflow_backend.data.evolution_product_effects_loader import (
    EVOLUTION_PRODUCT_EFFECTS_REGISTRY_V1,
    get_stage_product_effects,
    load_evolution_product_effects_registry_v1,
)
from todayflow_backend.services.evolution_user_state_v1 import (
    EVOLUTION_USER_STATE_V1_CONTRACT,
    validate_evolution_user_state_v1,
)

EVOLUTION_EFFECT_RUNTIME_POLICY_V1_CONTRACT = "evolution_effect_runtime_policy_v1"
EVOLUTION_EFFECT_RUNTIME_POLICY_V1_VERSION = "1.0.0"

POLICY_RESULT_CREATED = "created"
POLICY_RESULT_REJECTED = "rejected"

ALLOWED_EFFECT_GROUPS = frozenset(
    {
        "intelligence_effects",
        "engine_effects",
        "unlock_effects",
        "commerce_effects",
    }
)

ALWAYS_BLOCKED_EFFECT_KEYS = frozenset(
    {
        "stage_promotion",
        "automatic_reward",
        "automatic_unlock",
        "unlock_without_gate",
        "commerce_targeting",
        "commerce_activation",
        "profile_mutation",
        "memory_mutation",
        "llm_budget_escalation",
        "achievement_unlock",
    }
)

LLM_BUDGET_TIER_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3}

DEFAULT_SOURCE_SYSTEMS_READY: dict[str, bool] = {
    "practice_runtime": True,
    "goal_system": True,
    "calendar_intelligence": False,
    "share_features": False,
    "commerce_visibility": True,
    "active_knowledge": True,
}

UNLOCK_EFFECT_SOURCE_REQUIREMENTS: dict[str, str] = {
    "calendar_insight_tier": "calendar_intelligence",
    "goal_system_tier": "goal_system",
    "share_features": "share_features",
    "cycle_lengths_available": "practice_runtime",
    "practice_pack_tier": "practice_runtime",
    "path_themes_max_active": "practice_runtime",
}

EFFECT_LIMITS_KEYS = frozenset(
    {
        "context_slice_depth",
        "memory_window_days",
        "interpretation_level_max",
        "active_knowledge_cap",
        "llm_budget_tier",
        "max_context_lines",
        "llm_model_tier",
        "max_tokens_cap",
        "path_themes_max_active",
        "cycle_lengths_available",
        "practice_pack_tier",
        "calendar_insight_tier",
        "goal_system_tier",
        "share_features",
        "commerce_visibility",
        "symbolic_asset_tier",
    }
)

EVOLUTION_EFFECT_RUNTIME_POLICY_V1_KEYS = frozenset(
    {
        "contract_version",
        "policy_id",
        "user_id",
        "current_stage",
        "stage_effects_ref",
        "evolution_score_snapshot_id",
        "allowed_effects",
        "blocked_effects",
        "effect_limits",
        "requires_gate",
        "promotion_allowed",
        "profile_update_allowed",
        "memory_update_allowed",
        "commerce_activation_allowed",
        "created_at",
        "version",
    }
)

FORBIDDEN_POLICY_FIELDS = frozenset(
    {
        "promoted_stage",
        "stage_promoted_at",
        "evolution_score",
        "evolution_state",
        "achievement_id",
        "reward_id",
        "memory_write",
        "profile_update",
        "openapi_field",
        "ui_screen",
    }
)

FORBIDDEN_POLICY_FIELD_PATTERN = re.compile(
    r"(achievement|commerce_target|purchase|reward|badge|payment|subscription|promotion|memory_write|profile_update)",
    re.I,
)


class EvolutionEffectRuntimePolicyError(ValueError):
    """Raised when runtime policy inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _stage_effects_ref(stage_code: str, stage_effects: dict[str, Any]) -> str:
    version = stage_effects.get("version", "1.0.0")
    return f"{EVOLUTION_PRODUCT_EFFECTS_REGISTRY_V1}:{stage_code}:{version}"


def _build_effect_limits(stage_effects: dict[str, Any]) -> dict[str, Any]:
    intelligence = stage_effects.get("intelligence_effects") or {}
    engine = stage_effects.get("engine_effects") or {}
    unlock = stage_effects.get("unlock_effects") or {}
    commerce = stage_effects.get("commerce_effects") or {}

    return {
        "context_slice_depth": intelligence.get("context_slice_depth"),
        "memory_window_days": intelligence.get("memory_window_days"),
        "interpretation_level_max": intelligence.get("interpretation_level_max"),
        "active_knowledge_cap": intelligence.get("active_knowledge_cap"),
        "llm_budget_tier": engine.get("llm_budget_tier"),
        "max_context_lines": engine.get("max_context_lines"),
        "llm_model_tier": engine.get("llm_model_tier"),
        "max_tokens_cap": engine.get("max_tokens_cap"),
        "path_themes_max_active": unlock.get("path_themes_max_active"),
        "cycle_lengths_available": list(unlock.get("cycle_lengths_available") or []),
        "practice_pack_tier": unlock.get("practice_pack_tier"),
        "calendar_insight_tier": unlock.get("calendar_insight_tier"),
        "goal_system_tier": unlock.get("goal_system_tier"),
        "share_features": unlock.get("share_features"),
        "commerce_visibility": commerce.get("commerce_visibility"),
        "symbolic_asset_tier": commerce.get("symbolic_asset_tier"),
    }


def _commerce_visibility_only(commerce_effects: dict[str, Any]) -> dict[str, Any]:
    return {
        "commerce_visibility": commerce_effects.get("commerce_visibility"),
        "symbolic_asset_tier": commerce_effects.get("symbolic_asset_tier"),
        "themed_suggestions": commerce_effects.get("themed_suggestions"),
    }


def _unlock_effect_ready(
    unlock_effects: dict[str, Any],
    source_systems_ready: dict[str, bool],
) -> tuple[dict[str, Any], list[str]]:
    allowed: dict[str, Any] = {}
    blocked_keys: list[str] = []

    for key, value in unlock_effects.items():
        source = UNLOCK_EFFECT_SOURCE_REQUIREMENTS.get(key)
        if source is None:
            allowed[key] = value
            continue
        if key == "calendar_insight_tier" and value in {"none", None}:
            allowed[key] = value
            continue
        if key == "goal_system_tier" and value in {"none", None}:
            allowed[key] = value
            continue
        if key == "share_features" and value is False:
            allowed[key] = value
            continue
        if source_systems_ready.get(source, False):
            allowed[key] = value
        else:
            blocked_keys.append(f"unlock_effects.{key}")

    return allowed, blocked_keys


def _resolve_allowed_and_blocked_effects(
    stage_effects: dict[str, Any],
    *,
    gate_eligible: bool,
    source_systems_ready: dict[str, bool],
    requested_llm_budget_tier: str | None,
) -> tuple[dict[str, Any], list[str]]:
    intelligence = dict(stage_effects.get("intelligence_effects") or {})
    engine = dict(stage_effects.get("engine_effects") or {})
    unlock = dict(stage_effects.get("unlock_effects") or {})
    commerce = dict(stage_effects.get("commerce_effects") or {})

    blocked: list[str] = sorted(ALWAYS_BLOCKED_EFFECT_KEYS)

    if not gate_eligible:
        blocked.append("unlock_without_gate")
        unlock_allowed: dict[str, Any] = {}
        for key in unlock:
            blocked.append(f"unlock_effects.{key}")
    else:
        unlock_allowed, unlock_blocked = _unlock_effect_ready(unlock, source_systems_ready)
        blocked.extend(unlock_blocked)

    if requested_llm_budget_tier is not None:
        cap = engine.get("llm_budget_tier")
        requested_rank = LLM_BUDGET_TIER_ORDER.get(requested_llm_budget_tier, -1)
        cap_rank = LLM_BUDGET_TIER_ORDER.get(str(cap), -1)
        if requested_rank > cap_rank:
            blocked.append("llm_budget_escalation")

    allowed = {
        "intelligence_effects": intelligence,
        "engine_effects": engine,
        "unlock_effects": unlock_allowed,
        "commerce_effects": _commerce_visibility_only(commerce),
    }

    return allowed, sorted(set(blocked))


def try_build_evolution_effect_runtime_policy_v1(
    *,
    evolution_user_state: dict[str, Any],
    evolution_score_snapshot_id: str | None,
    source_systems_ready: dict[str, bool] | None = None,
    requested_llm_budget_tier: str | None = None,
    policy_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """
    Build read-only runtime policy: B1.2 state + B1.5 registry → allowed/blocked effects.

    Does not promote stage, mutate profile/memory, or activate commerce targeting.
    """
    if evolution_user_state.get("contract_version") != EVOLUTION_USER_STATE_V1_CONTRACT:
        return {
            "result": POLICY_RESULT_REJECTED,
            "policy": None,
            "reasons": ["invalid evolution_user_state contract_version"],
        }

    state_errors = validate_evolution_user_state_v1(evolution_user_state)
    if state_errors:
        return {
            "result": POLICY_RESULT_REJECTED,
            "policy": None,
            "reasons": state_errors[:8],
        }

    if evolution_user_state.get("status") != "active":
        return {
            "result": POLICY_RESULT_REJECTED,
            "policy": None,
            "reasons": ["user state status must be active"],
        }

    if not evolution_score_snapshot_id:
        return {
            "result": POLICY_RESULT_REJECTED,
            "policy": None,
            "reasons": ["evolution_score_snapshot_id required"],
        }

    current_stage = evolution_user_state.get("current_stage")
    if not isinstance(current_stage, str) or current_stage not in CANONICAL_STAGE_ORDER:
        return {
            "result": POLICY_RESULT_REJECTED,
            "policy": None,
            "reasons": [f"unknown current_stage: {current_stage!r}"],
        }

    cd = load_evolution_cd_v1()
    if current_stage not in (cd.get("evolution_stages") or {}):
        return {
            "result": POLICY_RESULT_REJECTED,
            "policy": None,
            "reasons": [f"current_stage not found in B1.1 CD: {current_stage!r}"],
        }

    try:
        stage_effects = get_stage_product_effects(current_stage)
    except Exception as exc:
        return {
            "result": POLICY_RESULT_REJECTED,
            "policy": None,
            "reasons": [str(exc)],
        }

    if stage_effects.get("status") == "draft":
        return {
            "result": POLICY_RESULT_REJECTED,
            "policy": None,
            "reasons": [f"stage product effects for {current_stage!r} are draft-only"],
        }

    readiness = dict(DEFAULT_SOURCE_SYSTEMS_READY)
    if source_systems_ready:
        readiness.update(source_systems_ready)

    eligibility = evolution_user_state.get("stage_gate_eligibility") or {}
    gate_eligible = bool(eligibility.get("eligible")) if isinstance(eligibility, dict) else False

    allowed_effects, blocked_effects = _resolve_allowed_and_blocked_effects(
        stage_effects,
        gate_eligible=gate_eligible,
        source_systems_ready=readiness,
        requested_llm_budget_tier=requested_llm_budget_tier,
    )

    policy = {
        "contract_version": EVOLUTION_EFFECT_RUNTIME_POLICY_V1_CONTRACT,
        "policy_id": policy_id or str(uuid4()),
        "user_id": evolution_user_state["user_id"],
        "current_stage": current_stage,
        "stage_effects_ref": _stage_effects_ref(current_stage, stage_effects),
        "evolution_score_snapshot_id": evolution_score_snapshot_id,
        "allowed_effects": allowed_effects,
        "blocked_effects": blocked_effects,
        "effect_limits": _build_effect_limits(stage_effects),
        "requires_gate": True,
        "promotion_allowed": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "commerce_activation_allowed": False,
        "created_at": created_at or _utc_now_iso(),
        "version": EVOLUTION_EFFECT_RUNTIME_POLICY_V1_VERSION,
    }

    errors = validate_evolution_effect_runtime_policy_v1(
        policy,
        stage_effects=stage_effects,
    )
    if errors:
        return {
            "result": POLICY_RESULT_REJECTED,
            "policy": None,
            "reasons": errors[:8],
        }

    return {
        "result": POLICY_RESULT_CREATED,
        "policy": policy,
        "reasons": [],
    }


def build_evolution_effect_runtime_policy_v1(
    *,
    evolution_user_state: dict[str, Any],
    evolution_score_snapshot_id: str | None,
    **kwargs: Any,
) -> dict[str, Any]:
    outcome = try_build_evolution_effect_runtime_policy_v1(
        evolution_user_state=evolution_user_state,
        evolution_score_snapshot_id=evolution_score_snapshot_id,
        **kwargs,
    )
    if outcome["result"] != POLICY_RESULT_CREATED:
        raise EvolutionEffectRuntimePolicyError("; ".join(outcome["reasons"]))
    assert outcome["policy"] is not None
    return outcome["policy"]


def validate_evolution_effect_runtime_policy_v1(
    policy: dict[str, Any],
    *,
    stage_effects: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []

    if policy.get("contract_version") != EVOLUTION_EFFECT_RUNTIME_POLICY_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in EVOLUTION_EFFECT_RUNTIME_POLICY_V1_KEYS:
        if key not in policy:
            errors.append(f"missing field: {key}")

    for key in policy:
        if key in FORBIDDEN_POLICY_FIELDS:
            errors.append(f"forbidden field: {key}")
        elif key not in {
            "promotion_allowed",
            "profile_update_allowed",
            "memory_update_allowed",
            "commerce_activation_allowed",
        } and FORBIDDEN_POLICY_FIELD_PATTERN.search(key):
            errors.append(f"forbidden field name: {key}")

    if policy.get("requires_gate") is not True:
        errors.append("requires_gate must be true")
    if policy.get("promotion_allowed") is not False:
        errors.append("promotion_allowed must be false")
    if policy.get("profile_update_allowed") is not False:
        errors.append("profile_update_allowed must be false")
    if policy.get("memory_update_allowed") is not False:
        errors.append("memory_update_allowed must be false")
    if policy.get("commerce_activation_allowed") is not False:
        errors.append("commerce_activation_allowed must be false")

    if not isinstance(policy.get("evolution_score_snapshot_id"), str) or not policy["evolution_score_snapshot_id"]:
        errors.append("evolution_score_snapshot_id must be non-empty string")

    allowed = policy.get("allowed_effects")
    if not isinstance(allowed, dict):
        errors.append("allowed_effects must be object")
    elif set(allowed.keys()) != ALLOWED_EFFECT_GROUPS:
        errors.append("allowed_effects groups invalid")
    else:
        if isinstance(allowed, dict):
            commerce = allowed.get("commerce_effects")
            if isinstance(commerce, dict) and "commerce_targeting" in commerce:
                errors.append("commerce targeting not allowed in allowed_effects")
        if isinstance(allowed, dict) and "stage_promotion" in allowed:
            errors.append("promotion must not appear in allowed_effects")

    blocked = policy.get("blocked_effects")
    if not isinstance(blocked, list):
        errors.append("blocked_effects must be array")
    else:
        for required in (
            "stage_promotion",
            "commerce_activation",
            "profile_mutation",
            "memory_mutation",
        ):
            if required not in blocked:
                errors.append(f"blocked_effects must include {required!r}")

    limits = policy.get("effect_limits")
    if not isinstance(limits, dict):
        errors.append("effect_limits must be object")
    elif set(limits.keys()) != EFFECT_LIMITS_KEYS:
        errors.append("effect_limits shape invalid")

    if stage_effects is not None and isinstance(limits, dict):
        expected = _build_effect_limits(stage_effects)
        if limits != expected:
            errors.append("effect_limits must mirror B1.5 registry caps")

        engine = allowed.get("engine_effects") if isinstance(allowed, dict) else None
        if isinstance(engine, dict):
            cap_tier = expected.get("llm_budget_tier")
            policy_tier = engine.get("llm_budget_tier")
            cap_rank = LLM_BUDGET_TIER_ORDER.get(str(cap_tier), -1)
            policy_rank = LLM_BUDGET_TIER_ORDER.get(str(policy_tier), -1)
            if policy_rank > cap_rank:
                errors.append("engine_effects llm_budget_tier exceeds B1.5 cap")

    current_stage = policy.get("current_stage")
    if isinstance(current_stage, str):
        try:
            load_evolution_product_effects_registry_v1()
            get_stage_product_effects(current_stage)
        except Exception as exc:
            errors.append(str(exc))

    return errors
