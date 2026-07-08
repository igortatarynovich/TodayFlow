"""B1.5 — Load and validate Evolution Product Effects registry."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.evolution_cd_loader import load_evolution_cd_v1
from todayflow_backend.data.evolution_cd_validator import (
    ALLOWED_COMMERCE_VISIBILITY,
    ALLOWED_CYCLE_LENGTHS,
    ALLOWED_LLM_BUDGET_TIERS,
    ALLOWED_STAGE_DEPTHS,
    CANONICAL_STAGE_ORDER,
)
from todayflow_backend.data.reference_machine_loader import DATA_ROOT

EVOLUTION_PRODUCT_EFFECTS_REGISTRY_V1 = "evolution_product_effects_registry_v1"

EVOLUTION_PRODUCT_EFFECTS_REGISTRY_PATH = (
    DATA_ROOT / "reference" / "evolution" / "evolution_product_effects_registry_v1.json"
)

ALLOWED_PROMPT_TONES = frozenset({"exploratory", "balanced", "concise"})
ALLOWED_ANSWER_LENGTHS = frozenset({"short", "normal", "deep"})
ALLOWED_INTERPRETATION_LEVELS = frozenset({"L1", "L2", "L3", "L4"})
ALLOWED_LLM_MODEL_TIERS = frozenset({"cheap", "standard", "premium"})
ALLOWED_MAX_TOKENS_CAPS = frozenset({"low", "medium", "high"})
ALLOWED_PRACTICE_PACK_TIERS = frozenset({"starter", "core", "advanced", "full"})
ALLOWED_CALENDAR_INSIGHT_TIERS = frozenset({"none", "basic", "standard", "full"})
ALLOWED_GOAL_SYSTEM_TIERS = frozenset({"none", "basic", "standard", "advanced"})
ALLOWED_SYMBOLIC_ASSET_TIERS = frozenset({"none", "soft", "themed", "full"})
ALLOWED_REGISTRY_STATUSES = frozenset({"draft", "active"})

INTERPRETATION_LEVEL_ORDER = {"L1": 1, "L2": 2, "L3": 3, "L4": 4}
MAX_TOKENS_ORDER = {"low": 1, "medium": 2, "high": 3}
PRACTICE_PACK_ORDER = {"starter": 1, "core": 2, "advanced": 3, "full": 4}
CALENDAR_INSIGHT_ORDER = {"none": 0, "basic": 1, "standard": 2, "full": 3}
GOAL_SYSTEM_ORDER = {"none": 0, "basic": 1, "standard": 2, "advanced": 3}
SYMBOLIC_ASSET_ORDER = {"none": 0, "soft": 1, "themed": 2, "full": 3}

INTELLIGENCE_EFFECTS_V1_KEYS = frozenset(
    {
        "context_slice_depth",
        "memory_window_days",
        "prompt_tone",
        "answer_length",
        "interpretation_level_max",
        "personalization_depth",
        "active_knowledge_cap",
    }
)

ENGINE_EFFECTS_V1_KEYS = frozenset(
    {
        "llm_budget_tier",
        "max_context_lines",
        "llm_model_tier",
        "max_tokens_cap",
    }
)

UNLOCK_EFFECTS_V1_KEYS = frozenset(
    {
        "path_themes_max_active",
        "cycle_lengths_available",
        "practice_pack_tier",
        "calendar_insight_tier",
        "goal_system_tier",
        "share_features",
    }
)

COMMERCE_EFFECTS_V1_KEYS = frozenset(
    {
        "commerce_visibility",
        "symbolic_asset_tier",
        "themed_suggestions",
    }
)

STAGE_PRODUCT_EFFECTS_V1_KEYS = frozenset(
    {
        "stage_code",
        "user_facing_summary",
        "intelligence_effects",
        "engine_effects",
        "unlock_effects",
        "commerce_effects",
        "status",
        "version",
    }
)

REGISTRY_TOP_KEYS = frozenset(
    {
        "contract_version",
        "domain",
        "version",
        "status",
        "description",
        "stage_product_effects",
    }
)

FORBIDDEN_PRODUCT_EFFECTS_FIELDS = frozenset(
    {
        "promotion_allowed",
        "api_exposure_allowed",
        "evolution_score",
        "stage_gate",
        "runtime_config",
        "ui_screen",
        "openapi_field",
    }
)

MONOTONIC_INT_FIELDS = (
    ("intelligence_effects", "memory_window_days"),
    ("intelligence_effects", "active_knowledge_cap"),
    ("unlock_effects", "path_themes_max_active"),
    ("engine_effects", "max_context_lines"),
)


class EvolutionProductEffectsError(Exception):
    """Raised when product effects registry is missing or invalid."""


def clear_evolution_product_effects_cache() -> None:
    load_evolution_product_effects_registry_v1.cache_clear()


@lru_cache(maxsize=1)
def load_evolution_product_effects_registry_v1() -> dict[str, Any]:
    path = Path(
        os.getenv(
            "TODAYFLOW_EVOLUTION_PRODUCT_EFFECTS_PATH",
            EVOLUTION_PRODUCT_EFFECTS_REGISTRY_PATH,
        )
    )
    if not path.is_file():
        raise EvolutionProductEffectsError(f"product effects registry not found: {path}")
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    errors = validate_evolution_product_effects_registry_v1(payload)
    if errors:
        raise EvolutionProductEffectsError("; ".join(errors[:8]))
    return payload


def get_stage_product_effects(
    stage_code: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = registry if registry is not None else load_evolution_product_effects_registry_v1()
    effects = (payload.get("stage_product_effects") or {}).get(stage_code)
    if not isinstance(effects, dict):
        raise EvolutionProductEffectsError(f"stage product effects not found: {stage_code!r}")
    return dict(effects)


def list_stage_product_effects_ordered(
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    payload = registry if registry is not None else load_evolution_product_effects_registry_v1()
    stages = payload.get("stage_product_effects") or {}
    return [dict(stages[code]) for code in CANONICAL_STAGE_ORDER if code in stages]


def diff_stage_product_effects_v1(
    from_stage: str,
    to_stage: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Read-only diff: what changes between two stages (reference helper, not runtime)."""
    payload = registry if registry is not None else load_evolution_product_effects_registry_v1()
    from_effects = get_stage_product_effects(from_stage, payload)
    to_effects = get_stage_product_effects(to_stage, payload)

    changed: dict[str, Any] = {}
    for section in ("intelligence_effects", "engine_effects", "unlock_effects", "commerce_effects"):
        before = from_effects.get(section) or {}
        after = to_effects.get(section) or {}
        if not isinstance(before, dict) or not isinstance(after, dict):
            continue
        section_changes: dict[str, dict[str, Any]] = {}
        for key in set(before.keys()) | set(after.keys()):
            if before.get(key) != after.get(key):
                section_changes[key] = {"from": before.get(key), "to": after.get(key)}
        if section_changes:
            changed[section] = section_changes

    return {
        "from_stage": from_stage,
        "to_stage": to_stage,
        "user_facing_summary_from": from_effects.get("user_facing_summary"),
        "user_facing_summary_to": to_effects.get("user_facing_summary"),
        "changed_effects": changed,
    }


def validate_evolution_product_effects_registry_v1(
    payload: dict[str, Any],
    *,
    evolution_cd: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []

    if payload.get("contract_version") != EVOLUTION_PRODUCT_EFFECTS_REGISTRY_V1:
        errors.append("invalid contract_version")

    for key in REGISTRY_TOP_KEYS:
        if key not in payload:
            errors.append(f"missing top-level field: {key}")

    if payload.get("domain") != "evolution":
        errors.append("domain must be evolution")

    for key in payload:
        if key in FORBIDDEN_PRODUCT_EFFECTS_FIELDS:
            errors.append(f"forbidden field: {key}")

    stages = payload.get("stage_product_effects")
    if not isinstance(stages, dict):
        errors.append("stage_product_effects must be object")
        return errors

    if len(stages) != len(CANONICAL_STAGE_ORDER):
        errors.append(f"expected {len(CANONICAL_STAGE_ORDER)} stage product effects")

    if set(stages.keys()) != set(CANONICAL_STAGE_ORDER):
        errors.append("stage_product_effects must match canonical stage set")

    cd = evolution_cd if evolution_cd is not None else load_evolution_cd_v1()
    cd_stages = cd.get("evolution_stages") or {}

    ordered_effects: list[dict[str, Any]] = []

    for code in CANONICAL_STAGE_ORDER:
        entry = stages.get(code)
        prefix = f"stage_product_effects[{code}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: must be object")
            continue

        ordered_effects.append(entry)

        for field in STAGE_PRODUCT_EFFECTS_V1_KEYS:
            if field not in entry:
                errors.append(f"{prefix}: missing field {field!r}")

        if entry.get("stage_code") != code:
            errors.append(f"{prefix}: stage_code mismatch")

        if entry.get("status") not in ALLOWED_REGISTRY_STATUSES:
            errors.append(f"{prefix}: invalid status")

        if code not in cd_stages:
            errors.append(f"{prefix}: unknown stage in B1.1 CD")
            continue

        cd_stage = cd_stages[code]
        errors.extend(_validate_effect_sections(entry, prefix))
        errors.extend(_validate_b1_1_alignment(entry, cd_stage, prefix))

    errors.extend(_validate_monotonic_progression(ordered_effects))

    return errors


def _validate_effect_sections(entry: dict[str, Any], prefix: str) -> list[str]:
    errors: list[str] = []

    intelligence = entry.get("intelligence_effects")
    if not isinstance(intelligence, dict):
        errors.append(f"{prefix}: intelligence_effects must be object")
    elif set(intelligence.keys()) != INTELLIGENCE_EFFECTS_V1_KEYS:
        errors.append(f"{prefix}: intelligence_effects shape invalid")
    else:
        if intelligence.get("context_slice_depth") not in ALLOWED_STAGE_DEPTHS:
            errors.append(f"{prefix}: invalid context_slice_depth")
        if intelligence.get("personalization_depth") not in ALLOWED_STAGE_DEPTHS:
            errors.append(f"{prefix}: invalid personalization_depth")
        if intelligence.get("prompt_tone") not in ALLOWED_PROMPT_TONES:
            errors.append(f"{prefix}: invalid prompt_tone")
        if intelligence.get("answer_length") not in ALLOWED_ANSWER_LENGTHS:
            errors.append(f"{prefix}: invalid answer_length")
        if intelligence.get("interpretation_level_max") not in ALLOWED_INTERPRETATION_LEVELS:
            errors.append(f"{prefix}: invalid interpretation_level_max")
        memory = intelligence.get("memory_window_days")
        if not isinstance(memory, int) or memory < 1:
            errors.append(f"{prefix}: memory_window_days must be positive int")
        cap = intelligence.get("active_knowledge_cap")
        if not isinstance(cap, int) or cap < 0 or cap > 5:
            errors.append(f"{prefix}: active_knowledge_cap must be 0..5")

    engine = entry.get("engine_effects")
    if not isinstance(engine, dict):
        errors.append(f"{prefix}: engine_effects must be object")
    elif set(engine.keys()) != ENGINE_EFFECTS_V1_KEYS:
        errors.append(f"{prefix}: engine_effects shape invalid")
    else:
        if engine.get("llm_budget_tier") not in ALLOWED_LLM_BUDGET_TIERS:
            errors.append(f"{prefix}: invalid llm_budget_tier")
        if engine.get("llm_model_tier") not in ALLOWED_LLM_MODEL_TIERS:
            errors.append(f"{prefix}: invalid llm_model_tier")
        if engine.get("max_tokens_cap") not in ALLOWED_MAX_TOKENS_CAPS:
            errors.append(f"{prefix}: invalid max_tokens_cap")
        lines = engine.get("max_context_lines")
        if not isinstance(lines, int) or lines < 0 or lines > 10:
            errors.append(f"{prefix}: max_context_lines invalid")

    unlock = entry.get("unlock_effects")
    if not isinstance(unlock, dict):
        errors.append(f"{prefix}: unlock_effects must be object")
    elif set(unlock.keys()) != UNLOCK_EFFECTS_V1_KEYS:
        errors.append(f"{prefix}: unlock_effects shape invalid")
    else:
        if unlock.get("practice_pack_tier") not in ALLOWED_PRACTICE_PACK_TIERS:
            errors.append(f"{prefix}: invalid practice_pack_tier")
        if unlock.get("calendar_insight_tier") not in ALLOWED_CALENDAR_INSIGHT_TIERS:
            errors.append(f"{prefix}: invalid calendar_insight_tier")
        if unlock.get("goal_system_tier") not in ALLOWED_GOAL_SYSTEM_TIERS:
            errors.append(f"{prefix}: invalid goal_system_tier")
        if not isinstance(unlock.get("share_features"), bool):
            errors.append(f"{prefix}: share_features must be bool")
        max_paths = unlock.get("path_themes_max_active")
        if not isinstance(max_paths, int) or max_paths < 1 or max_paths > 10:
            errors.append(f"{prefix}: path_themes_max_active invalid")
        lengths = unlock.get("cycle_lengths_available")
        if not isinstance(lengths, list) or not lengths:
            errors.append(f"{prefix}: cycle_lengths_available required")
        else:
            for length in lengths:
                if length not in ALLOWED_CYCLE_LENGTHS:
                    errors.append(f"{prefix}: invalid cycle length {length!r}")

    commerce = entry.get("commerce_effects")
    if not isinstance(commerce, dict):
        errors.append(f"{prefix}: commerce_effects must be object")
    elif set(commerce.keys()) != COMMERCE_EFFECTS_V1_KEYS:
        errors.append(f"{prefix}: commerce_effects shape invalid")
    else:
        if commerce.get("commerce_visibility") not in ALLOWED_COMMERCE_VISIBILITY:
            errors.append(f"{prefix}: invalid commerce_visibility")
        if commerce.get("symbolic_asset_tier") not in ALLOWED_SYMBOLIC_ASSET_TIERS:
            errors.append(f"{prefix}: invalid symbolic_asset_tier")
        if not isinstance(commerce.get("themed_suggestions"), bool):
            errors.append(f"{prefix}: themed_suggestions must be bool")

    return errors


def _validate_b1_1_alignment(
    entry: dict[str, Any],
    cd_stage: dict[str, Any],
    prefix: str,
) -> list[str]:
    errors: list[str] = []
    engine = entry.get("engine_effects") or {}
    commerce = entry.get("commerce_effects") or {}
    intelligence = entry.get("intelligence_effects") or {}

    if engine.get("llm_budget_tier") != cd_stage.get("llm_budget_tier"):
        errors.append(f"{prefix}: llm_budget_tier must match B1.1 stage CD")
    if engine.get("max_context_lines") != cd_stage.get("max_context_lines"):
        errors.append(f"{prefix}: max_context_lines must match B1.1 stage CD")
    if commerce.get("commerce_visibility") != cd_stage.get("commerce_visibility"):
        errors.append(f"{prefix}: commerce_visibility must match B1.1 stage CD")
    if intelligence.get("context_slice_depth") != cd_stage.get("allowed_depth"):
        errors.append(f"{prefix}: context_slice_depth must match B1.1 allowed_depth")

    return errors


def _validate_monotonic_progression(ordered_effects: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []

    for index in range(1, len(ordered_effects)):
        prev = ordered_effects[index - 1]
        curr = ordered_effects[index]
        prev_code = prev.get("stage_code", "?")
        curr_code = curr.get("stage_code", "?")

        for section, field in MONOTONIC_INT_FIELDS:
            prev_section = prev.get(section) or {}
            curr_section = curr.get(section) or {}
            if not isinstance(prev_section, dict) or not isinstance(curr_section, dict):
                continue
            prev_val = prev_section.get(field)
            curr_val = curr_section.get(field)
            if isinstance(prev_val, int) and isinstance(curr_val, int) and curr_val < prev_val:
                errors.append(
                    f"non-monotonic {section}.{field}: {prev_code}={prev_val} -> {curr_code}={curr_val}"
                )

        prev_intel = prev.get("intelligence_effects") or {}
        curr_intel = curr.get("intelligence_effects") or {}
        prev_level = INTERPRETATION_LEVEL_ORDER.get(prev_intel.get("interpretation_level_max"), 0)
        curr_level = INTERPRETATION_LEVEL_ORDER.get(curr_intel.get("interpretation_level_max"), 0)
        if curr_level < prev_level:
            errors.append(
                f"non-monotonic interpretation_level_max: {prev_code} -> {curr_code}"
            )

    return errors
