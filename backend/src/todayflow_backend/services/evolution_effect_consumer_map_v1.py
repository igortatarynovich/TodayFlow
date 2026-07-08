"""B1.7 — Evolution effect consumer map (read-only policy slices per consumer)."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.evolution_effect_runtime_policy_v1 import (
    EVOLUTION_EFFECT_RUNTIME_POLICY_V1_CONTRACT,
    validate_evolution_effect_runtime_policy_v1,
)

EVOLUTION_EFFECT_CONSUMER_MAP_V1_CONTRACT = "evolution_effect_consumer_map_v1"
EVOLUTION_EFFECT_CONSUMER_SLICE_V1_CONTRACT = "evolution_effect_consumer_slice_v1"
EVOLUTION_EFFECT_CONSUMER_SLICE_V1_VERSION = "1.0.0"

SLICE_RESULT_CREATED = "created"
SLICE_RESULT_REJECTED = "rejected"

CONSUMER_DAY_ENGINE = "day_engine"
CONSUMER_CONTEXT_SELECTOR = "context_selector"
CONSUMER_LLM_GATE = "llm_gate"
CONSUMER_PRACTICE_SELECTOR = "practice_selector"
CONSUMER_CALENDAR = "calendar"
CONSUMER_COMMERCE_VISIBILITY = "commerce_visibility"

ALLOWED_CONSUMER_IDS = frozenset(
    {
        CONSUMER_DAY_ENGINE,
        CONSUMER_CONTEXT_SELECTOR,
        CONSUMER_LLM_GATE,
        CONSUMER_PRACTICE_SELECTOR,
        CONSUMER_CALENDAR,
        CONSUMER_COMMERCE_VISIBILITY,
    }
)

FORBIDDEN_SLICE_POLICY_FIELDS = frozenset(
    {
        "blocked_effects",
        "stage_effects_ref",
        "evolution_score_snapshot_id",
        "requires_gate",
    }
)

FORBIDDEN_SLICE_FIELD_PATTERN = re.compile(
    r"(blocked_effects|stage_effects_ref|evolution_score_snapshot|promotion|profile_update|memory_update|commerce_activation)",
    re.I,
)

EVOLUTION_EFFECT_CONSUMER_SLICE_V1_KEYS = frozenset(
    {
        "contract_version",
        "slice_id",
        "policy_id",
        "user_id",
        "consumer_id",
        "current_stage",
        "effect_limits",
        "allowed_effects",
        "read_only",
        "mutation_allowed",
        "profile_update_allowed",
        "memory_update_allowed",
        "commerce_activation_allowed",
        "created_at",
        "version",
    }
)

ConsumerSliceSpec = dict[str, Any]

CONSUMER_SLICE_SPECS: dict[str, ConsumerSliceSpec] = {
    CONSUMER_DAY_ENGINE: {
        "policy_metadata_fields": ("policy_id", "user_id", "current_stage"),
        "effect_limit_keys": ("max_context_lines", "context_slice_depth"),
        "allowed_effect_groups": {
            "engine_effects": ("max_context_lines", "llm_budget_tier"),
        },
    },
    CONSUMER_CONTEXT_SELECTOR: {
        "policy_metadata_fields": ("policy_id", "user_id", "current_stage"),
        "effect_limit_keys": (
            "context_slice_depth",
            "memory_window_days",
            "interpretation_level_max",
            "active_knowledge_cap",
        ),
        "allowed_effect_groups": {
            "intelligence_effects": (
                "context_slice_depth",
                "memory_window_days",
                "prompt_tone",
                "answer_length",
                "interpretation_level_max",
                "personalization_depth",
                "active_knowledge_cap",
            ),
        },
    },
    CONSUMER_LLM_GATE: {
        "policy_metadata_fields": ("policy_id", "user_id", "current_stage"),
        "effect_limit_keys": (
            "llm_budget_tier",
            "max_context_lines",
            "llm_model_tier",
            "max_tokens_cap",
        ),
        "allowed_effect_groups": {
            "engine_effects": (
                "llm_budget_tier",
                "max_context_lines",
                "llm_model_tier",
                "max_tokens_cap",
            ),
        },
    },
    CONSUMER_PRACTICE_SELECTOR: {
        "policy_metadata_fields": ("policy_id", "user_id", "current_stage"),
        "effect_limit_keys": (
            "path_themes_max_active",
            "cycle_lengths_available",
            "practice_pack_tier",
            "goal_system_tier",
        ),
        "allowed_effect_groups": {
            "unlock_effects": (
                "path_themes_max_active",
                "cycle_lengths_available",
                "practice_pack_tier",
                "goal_system_tier",
            ),
        },
    },
    CONSUMER_CALENDAR: {
        "policy_metadata_fields": ("policy_id", "user_id", "current_stage"),
        "effect_limit_keys": ("calendar_insight_tier", "cycle_lengths_available"),
        "allowed_effect_groups": {
            "unlock_effects": ("calendar_insight_tier", "cycle_lengths_available"),
        },
    },
    CONSUMER_COMMERCE_VISIBILITY: {
        "policy_metadata_fields": ("policy_id", "user_id", "current_stage"),
        "effect_limit_keys": ("commerce_visibility", "symbolic_asset_tier"),
        "allowed_effect_groups": {
            "commerce_effects": (
                "commerce_visibility",
                "symbolic_asset_tier",
                "themed_suggestions",
            ),
        },
    },
}


class EvolutionEffectConsumerMapError(ValueError):
    """Raised when consumer map inputs or slice payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def list_registered_consumers_v1() -> list[str]:
    return sorted(ALLOWED_CONSUMER_IDS)


def get_consumer_slice_spec_v1(consumer_id: str) -> ConsumerSliceSpec:
    spec = CONSUMER_SLICE_SPECS.get(consumer_id)
    if spec is None:
        raise EvolutionEffectConsumerMapError(f"unknown consumer_id: {consumer_id!r}")
    return spec


def _pick_mapping(source: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {key: source[key] for key in keys if key in source}


def _pick_allowed_effects(
    policy_allowed: dict[str, Any],
    allowed_effect_groups: dict[str, tuple[str, ...]],
) -> dict[str, Any]:
    picked: dict[str, Any] = {}
    for group, fields in allowed_effect_groups.items():
        group_data = policy_allowed.get(group)
        if not isinstance(group_data, dict):
            continue
        subset = _pick_mapping(group_data, fields)
        if subset:
            picked[group] = subset
    return picked


def try_extract_evolution_effect_consumer_slice_v1(
    policy: dict[str, Any],
    consumer_id: str,
    *,
    slice_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """
    Extract a read-only consumer slice from B1.6 policy.

    Does not apply effects or mutate profile/memory/personalization.
    """
    if policy.get("contract_version") != EVOLUTION_EFFECT_RUNTIME_POLICY_V1_CONTRACT:
        return {
            "result": SLICE_RESULT_REJECTED,
            "slice": None,
            "reasons": ["invalid policy contract_version"],
        }

    policy_errors = validate_evolution_effect_runtime_policy_v1(policy)
    if policy_errors:
        return {
            "result": SLICE_RESULT_REJECTED,
            "slice": None,
            "reasons": policy_errors[:8],
        }

    if consumer_id not in ALLOWED_CONSUMER_IDS:
        return {
            "result": SLICE_RESULT_REJECTED,
            "slice": None,
            "reasons": [f"unknown consumer_id: {consumer_id!r}"],
        }

    spec = CONSUMER_SLICE_SPECS[consumer_id]
    policy_limits = policy.get("effect_limits") or {}
    policy_allowed = policy.get("allowed_effects") or {}

    if not isinstance(policy_limits, dict):
        return {
            "result": SLICE_RESULT_REJECTED,
            "slice": None,
            "reasons": ["policy effect_limits must be object"],
        }
    if not isinstance(policy_allowed, dict):
        return {
            "result": SLICE_RESULT_REJECTED,
            "slice": None,
            "reasons": ["policy allowed_effects must be object"],
        }

    effect_limits = _pick_mapping(policy_limits, tuple(spec["effect_limit_keys"]))
    allowed_effects = _pick_allowed_effects(
        policy_allowed,
        spec["allowed_effect_groups"],
    )

    slice_payload = {
        "contract_version": EVOLUTION_EFFECT_CONSUMER_SLICE_V1_CONTRACT,
        "slice_id": slice_id or str(uuid4()),
        "policy_id": policy["policy_id"],
        "user_id": policy["user_id"],
        "consumer_id": consumer_id,
        "current_stage": policy["current_stage"],
        "effect_limits": effect_limits,
        "allowed_effects": allowed_effects,
        "read_only": True,
        "mutation_allowed": False,
        "profile_update_allowed": False,
        "memory_update_allowed": False,
        "commerce_activation_allowed": False,
        "created_at": created_at or _utc_now_iso(),
        "version": EVOLUTION_EFFECT_CONSUMER_SLICE_V1_VERSION,
    }

    errors = validate_evolution_effect_consumer_slice_v1(
        slice_payload,
        policy=policy,
        consumer_id=consumer_id,
    )
    if errors:
        return {
            "result": SLICE_RESULT_REJECTED,
            "slice": None,
            "reasons": errors[:8],
        }

    return {
        "result": SLICE_RESULT_CREATED,
        "slice": slice_payload,
        "reasons": [],
    }


def extract_evolution_effect_consumer_slice_v1(
    policy: dict[str, Any],
    consumer_id: str,
    **kwargs: Any,
) -> dict[str, Any]:
    outcome = try_extract_evolution_effect_consumer_slice_v1(
        policy,
        consumer_id,
        **kwargs,
    )
    if outcome["result"] != SLICE_RESULT_CREATED:
        raise EvolutionEffectConsumerMapError("; ".join(outcome["reasons"]))
    assert outcome["slice"] is not None
    return outcome["slice"]


def validate_evolution_effect_consumer_map_v1() -> list[str]:
    """Validate static consumer registry definitions."""
    errors: list[str] = []

    if set(CONSUMER_SLICE_SPECS.keys()) != ALLOWED_CONSUMER_IDS:
        errors.append("consumer slice specs must cover all registered consumers")

    for consumer_id, spec in CONSUMER_SLICE_SPECS.items():
        prefix = f"consumer[{consumer_id}]"
        metadata = spec.get("policy_metadata_fields")
        limit_keys = spec.get("effect_limit_keys")
        groups = spec.get("allowed_effect_groups")
        if not isinstance(metadata, tuple) or not metadata:
            errors.append(f"{prefix}: policy_metadata_fields required")
        if not isinstance(limit_keys, tuple):
            errors.append(f"{prefix}: effect_limit_keys must be tuple")
        if not isinstance(groups, dict) or not groups:
            errors.append(f"{prefix}: allowed_effect_groups required")
        elif isinstance(groups, dict):
            for group, fields in groups.items():
                if not isinstance(fields, tuple) or not fields:
                    errors.append(f"{prefix}: allowed_effect_groups[{group!r}] invalid")

    return errors


def validate_evolution_effect_consumer_slice_v1(
    slice_payload: dict[str, Any],
    *,
    policy: dict[str, Any] | None = None,
    consumer_id: str | None = None,
) -> list[str]:
    errors: list[str] = []

    if slice_payload.get("contract_version") != EVOLUTION_EFFECT_CONSUMER_SLICE_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in EVOLUTION_EFFECT_CONSUMER_SLICE_V1_KEYS:
        if key not in slice_payload:
            errors.append(f"missing field: {key}")

    for key in slice_payload:
        if key in FORBIDDEN_SLICE_POLICY_FIELDS:
            errors.append(f"forbidden policy field leaked into slice: {key}")
        elif key not in EVOLUTION_EFFECT_CONSUMER_SLICE_V1_KEYS and FORBIDDEN_SLICE_FIELD_PATTERN.search(key):
            errors.append(f"forbidden field name: {key}")

    resolved_consumer = consumer_id or slice_payload.get("consumer_id")
    if resolved_consumer not in ALLOWED_CONSUMER_IDS:
        errors.append("invalid consumer_id")
    else:
        spec = CONSUMER_SLICE_SPECS[resolved_consumer]
        limits = slice_payload.get("effect_limits")
        if not isinstance(limits, dict):
            errors.append("effect_limits must be object")
        elif isinstance(limits, dict):
            allowed_limit_keys = set(spec["effect_limit_keys"])
            if not set(limits.keys()).issubset(allowed_limit_keys):
                errors.append("effect_limits contains fields outside consumer map")

        allowed = slice_payload.get("allowed_effects")
        if not isinstance(allowed, dict):
            errors.append("allowed_effects must be object")
        elif isinstance(allowed, dict):
            allowed_groups = spec["allowed_effect_groups"]
            if not set(allowed.keys()).issubset(set(allowed_groups.keys())):
                errors.append("allowed_effects groups outside consumer map")
            for group, fields in allowed.items():
                expected_fields = set(allowed_groups.get(group, ()))
                if not isinstance(fields, dict):
                    errors.append(f"allowed_effects.{group} must be object")
                elif not set(fields.keys()).issubset(expected_fields):
                    errors.append(f"allowed_effects.{group} contains fields outside consumer map")

    if slice_payload.get("read_only") is not True:
        errors.append("read_only must be true")
    if slice_payload.get("mutation_allowed") is not False:
        errors.append("mutation_allowed must be false")
    if slice_payload.get("profile_update_allowed") is not False:
        errors.append("profile_update_allowed must be false")
    if slice_payload.get("memory_update_allowed") is not False:
        errors.append("memory_update_allowed must be false")
    if slice_payload.get("commerce_activation_allowed") is not False:
        errors.append("commerce_activation_allowed must be false")

    if policy is not None and resolved_consumer in ALLOWED_CONSUMER_IDS:
        for forbidden in (
            "blocked_effects",
            "stage_effects_ref",
            "evolution_score_snapshot_id",
        ):
            if forbidden in slice_payload:
                errors.append(f"slice must not expose {forbidden}")
        if slice_payload.get("policy_id") != policy.get("policy_id"):
            errors.append("slice policy_id must match source policy")
        if slice_payload.get("user_id") != policy.get("user_id"):
            errors.append("slice user_id must match source policy")

        full_policy_keys = set(policy.keys()) - {"contract_version", "version", "created_at"}
        slice_sensitive = set(slice_payload.keys()) & full_policy_keys
        leaked = slice_sensitive & {
            "blocked_effects",
            "stage_effects_ref",
            "evolution_score_snapshot_id",
            "requires_gate",
        }
        if leaked:
            errors.append(f"slice leaks full policy fields: {sorted(leaked)}")

    return errors


def build_evolution_effect_consumer_map_v1() -> dict[str, Any]:
    """Return read-only registry of consumer → allowed field paths."""
    errors = validate_evolution_effect_consumer_map_v1()
    if errors:
        raise EvolutionEffectConsumerMapError("; ".join(errors[:8]))

    consumers: dict[str, Any] = {}
    for consumer_id in sorted(ALLOWED_CONSUMER_IDS):
        spec = CONSUMER_SLICE_SPECS[consumer_id]
        consumers[consumer_id] = {
            "consumer_id": consumer_id,
            "policy_metadata_fields": list(spec["policy_metadata_fields"]),
            "effect_limit_keys": list(spec["effect_limit_keys"]),
            "allowed_effect_groups": {
                group: list(fields)
                for group, fields in spec["allowed_effect_groups"].items()
            },
            "read_only": True,
            "mutation_allowed": False,
        }

    return {
        "contract_version": EVOLUTION_EFFECT_CONSUMER_MAP_V1_CONTRACT,
        "consumers": consumers,
        "version": EVOLUTION_EFFECT_CONSUMER_SLICE_V1_VERSION,
    }
