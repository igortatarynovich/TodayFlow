"""C1.5 — Validate Ritual Definition registry (containers linking C1.1/C1.2/C1.4)."""

from __future__ import annotations

import re
from typing import Any

from todayflow_backend.data.evolution_cd_validator import (
    ALLOWED_PROGRESSION_SIGNAL_TYPES,
    CANONICAL_STAGE_ORDER,
    FORBIDDEN_GATE_SIGNAL_PATTERN,
)

RITUAL_DEFINITION_REGISTRY_V1_CONTRACT = "ritual_definition_registry_v1"

ALLOWED_REGISTRY_STATUSES = frozenset({"draft", "active"})

ALLOWED_RITUAL_CATEGORIES = frozenset(
    {
        "morning",
        "evening",
        "focus",
        "recovery",
        "reflection",
        "discipline",
    }
)

ALLOWED_SEQUENCE_TYPES = frozenset({"ordered", "flexible"})

ALLOWED_RITUAL_FREQUENCIES = frozenset({"daily", "weekly", "custom"})

ALLOWED_COMPONENT_TYPES = frozenset({"practice", "habit", "ascetic"})

ALLOWED_DIFFICULTY_LEVELS = frozenset({"beginner", "intermediate", "advanced"})

ALLOWED_COMPLETION_PERIODS = frozenset({"day", "week"})

RITUAL_DEFINITION_ALLOWED_SIGNALS = frozenset(
    {
        "practice_completed",
        "ritual_streak_confirmed",
    }
)

CANONICAL_RITUAL_DEFINITION_CODES: tuple[str, ...] = (
    "morning_grounding_ritual",
    "evening_reflection_ritual",
    "focus_start_ritual",
    "recovery_evening_ritual",
    "discipline_reset_ritual",
    "clarity_journaling_ritual",
    "body_energy_ritual",
    "no_phone_evening_ritual",
)

FORBIDDEN_RITUAL_FIELD_NAMES = frozenset(
    {
        "goal_type",
        "target_metric",
        "horizon",
        "cycle_length_days",
        "frequency_type",
        "linked_practice_definition_code",
        "instruction_text",
        "ui_text",
        "llm_prompt",
    }
)

FORBIDDEN_RITUAL_CONTENT_PATTERN = re.compile(
    r"(achievement|commerce|unlock|purchase|reward|badge|payment|subscription|llm.?prompt|ui.?card|variant.?text|instruction.?text)",
    re.I,
)

COMPONENT_V1_KEYS = frozenset(
    {
        "component_type",
        "component_code",
        "required",
        "order",
        "minimum_required_for_completion",
    }
)

MINIMUM_COMPLETION_RULE_V1_KEYS = frozenset(
    {
        "components_required",
        "period",
    }
)

DURATION_RANGE_V1_KEYS = frozenset({"min_minutes", "max_minutes"})

RITUAL_DEFINITION_V1_KEYS = frozenset(
    {
        "code",
        "title",
        "ritual_category",
        "description",
        "components",
        "component_count",
        "sequence_type",
        "recommended_frequency",
        "minimum_completion_rule",
        "compatible_paths",
        "compatible_stages",
        "suggested_duration_range",
        "produces_signals",
        "difficulty_level",
        "status",
        "version",
    }
)

RITUAL_DEFINITION_REGISTRY_V1_TOP_KEYS = frozenset(
    {
        "contract_version",
        "domain",
        "version",
        "status",
        "description",
        "ritual_definitions",
    }
)


class RitualDefinitionRegistryValidationError(Exception):
    """Raised when ritual definition registry payload fails validation."""


def _scan_forbidden_content(value: str, prefix: str, errors: list[str]) -> None:
    if FORBIDDEN_RITUAL_CONTENT_PATTERN.search(value):
        errors.append(f"{prefix}: forbidden achievement/commerce/content marker in text")
    if FORBIDDEN_GATE_SIGNAL_PATTERN.search(value):
        errors.append(f"{prefix}: forbidden achievement/commerce marker in text")


def _validate_component(
    component: Any,
    *,
    prefix: str,
    sequence_type: str,
    practice_codes: frozenset[str] | None,
    habit_codes: frozenset[str] | None,
    ascetic_codes: frozenset[str] | None,
    errors: list[str],
) -> None:
    if not isinstance(component, dict):
        errors.append(f"{prefix}: must be object")
        return

    extra_keys = set(component.keys()) - COMPONENT_V1_KEYS
    if extra_keys:
        errors.append(f"{prefix}: unexpected component fields {sorted(extra_keys)}")

    for field in COMPONENT_V1_KEYS:
        if field not in component:
            errors.append(f"{prefix}: missing component field {field!r}")

    comp_type = component.get("component_type")
    comp_code = component.get("component_code")
    if comp_type not in ALLOWED_COMPONENT_TYPES:
        errors.append(f"{prefix}: invalid component_type")
    elif isinstance(comp_code, str):
        if comp_type == "practice" and practice_codes is not None and comp_code not in practice_codes:
            errors.append(f"{prefix}: unknown practice component_code {comp_code!r}")
        if comp_type == "habit" and habit_codes is not None and comp_code not in habit_codes:
            errors.append(f"{prefix}: unknown habit component_code {comp_code!r}")
        if comp_type == "ascetic" and ascetic_codes is not None and comp_code not in ascetic_codes:
            errors.append(f"{prefix}: unknown ascetic component_code {comp_code!r}")
    else:
        errors.append(f"{prefix}: component_code must be string")

    if not isinstance(component.get("required"), bool):
        errors.append(f"{prefix}: required must be boolean")

    if not isinstance(component.get("minimum_required_for_completion"), bool):
        errors.append(f"{prefix}: minimum_required_for_completion must be boolean")

    order = component.get("order")
    is_required = component.get("required") is True
    if sequence_type == "ordered" and is_required:
        if not isinstance(order, int) or order < 1:
            errors.append(f"{prefix}: required component must have positive order when sequence_type is ordered")
    elif order is not None and not isinstance(order, int):
        errors.append(f"{prefix}: order must be int or null")


def validate_ritual_definition_registry_v1(
    payload: dict[str, Any],
    *,
    path_theme_codes: frozenset[str] | None = None,
    practice_codes: frozenset[str] | None = None,
    habit_codes: frozenset[str] | None = None,
    ascetic_codes: frozenset[str] | None = None,
) -> list[str]:
    errors: list[str] = []

    if payload.get("contract_version") != RITUAL_DEFINITION_REGISTRY_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in RITUAL_DEFINITION_REGISTRY_V1_TOP_KEYS:
        if key not in payload:
            errors.append(f"missing top-level field: {key}")

    if payload.get("domain") != "practice":
        errors.append("domain must be practice")

    if payload.get("status") not in ALLOWED_REGISTRY_STATUSES:
        errors.append("invalid top-level status")

    definitions = payload.get("ritual_definitions")
    if not isinstance(definitions, dict):
        errors.append("ritual_definitions must be object")
        return errors

    expected_codes = set(CANONICAL_RITUAL_DEFINITION_CODES)
    if set(definitions.keys()) != expected_codes:
        missing = expected_codes - set(definitions.keys())
        extra = set(definitions.keys()) - expected_codes
        if missing:
            errors.append(f"missing ritual definitions: {sorted(missing)}")
        if extra:
            errors.append(f"unexpected ritual definitions: {sorted(extra)}")

    for code, entry in definitions.items():
        prefix = f"ritual_definition[{code}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: must be object")
            continue

        forbidden_present = set(entry.keys()) & FORBIDDEN_RITUAL_FIELD_NAMES
        if forbidden_present:
            errors.append(f"{prefix}: forbidden goal/cycle/content fields {sorted(forbidden_present)}")

        extra_keys = set(entry.keys()) - RITUAL_DEFINITION_V1_KEYS
        if extra_keys:
            errors.append(f"{prefix}: unexpected fields {sorted(extra_keys)}")

        for field in RITUAL_DEFINITION_V1_KEYS:
            if field not in entry:
                errors.append(f"{prefix}: missing field {field!r}")

        if entry.get("code") != code:
            errors.append(f"{prefix}: code mismatch")

        title = entry.get("title")
        if isinstance(title, str):
            _scan_forbidden_content(title, prefix, errors)
        else:
            errors.append(f"{prefix}: title must be string")

        description = entry.get("description")
        if isinstance(description, str) and description.strip():
            _scan_forbidden_content(description, prefix, errors)
        else:
            errors.append(f"{prefix}: description must be non-empty string")

        if entry.get("ritual_category") not in ALLOWED_RITUAL_CATEGORIES:
            errors.append(f"{prefix}: invalid ritual_category")

        sequence_type = entry.get("sequence_type")
        if sequence_type not in ALLOWED_SEQUENCE_TYPES:
            errors.append(f"{prefix}: invalid sequence_type")
            sequence_type = ""

        if entry.get("recommended_frequency") not in ALLOWED_RITUAL_FREQUENCIES:
            errors.append(f"{prefix}: invalid recommended_frequency")

        components = entry.get("components")
        component_count = entry.get("component_count")
        if not isinstance(components, list) or not components:
            errors.append(f"{prefix}: components must be non-empty list")
        elif not isinstance(component_count, int) or component_count < 1:
            errors.append(f"{prefix}: component_count must be positive int")
        elif len(components) != component_count:
            errors.append(f"{prefix}: component_count must match len(components)")

        if isinstance(components, list) and isinstance(sequence_type, str):
            orders = []
            flagged_count = 0
            for index, component in enumerate(components):
                comp_prefix = f"{prefix}.components[{index}]"
                _validate_component(
                    component,
                    prefix=comp_prefix,
                    sequence_type=sequence_type,
                    practice_codes=practice_codes,
                    habit_codes=habit_codes,
                    ascetic_codes=ascetic_codes,
                    errors=errors,
                )
                if isinstance(component, dict):
                    if component.get("minimum_required_for_completion") is True:
                        flagged_count += 1
                    order = component.get("order")
                    if isinstance(order, int):
                        orders.append(order)

            if sequence_type == "ordered" and orders and len(orders) != len(set(orders)):
                errors.append(f"{prefix}: component order values must be unique when set")

        rule = entry.get("minimum_completion_rule")
        if not isinstance(rule, dict) or not rule:
            errors.append(f"{prefix}: minimum_completion_rule must be non-empty object")
        else:
            if set(rule.keys()) != MINIMUM_COMPLETION_RULE_V1_KEYS:
                errors.append(f"{prefix}: minimum_completion_rule has invalid keys")
            components_required = rule.get("components_required")
            if not isinstance(components_required, int) or components_required < 1:
                errors.append(f"{prefix}: minimum_completion_rule.components_required must be positive int")
            if rule.get("period") not in ALLOWED_COMPLETION_PERIODS:
                errors.append(f"{prefix}: minimum_completion_rule.period invalid")
            if isinstance(components, list) and isinstance(components_required, int):
                if components_required > len(components):
                    errors.append(f"{prefix}: components_required cannot exceed component_count")
                if flagged_count > 0 and components_required > flagged_count:
                    errors.append(
                        f"{prefix}: components_required cannot exceed minimum_required_for_completion count"
                    )

        duration = entry.get("suggested_duration_range")
        if not isinstance(duration, dict):
            errors.append(f"{prefix}: suggested_duration_range must be object")
        else:
            if set(duration.keys()) != DURATION_RANGE_V1_KEYS:
                errors.append(f"{prefix}: suggested_duration_range must have min_minutes and max_minutes")
            min_m = duration.get("min_minutes")
            max_m = duration.get("max_minutes")
            if not isinstance(min_m, int) or min_m < 1:
                errors.append(f"{prefix}: suggested_duration_range.min_minutes must be positive int")
            if not isinstance(max_m, int) or max_m < 1:
                errors.append(f"{prefix}: suggested_duration_range.max_minutes must be positive int")
            if isinstance(min_m, int) and isinstance(max_m, int) and min_m > max_m:
                errors.append(f"{prefix}: suggested_duration_range min must be <= max")

        paths = entry.get("compatible_paths")
        if not isinstance(paths, list) or not paths:
            errors.append(f"{prefix}: compatible_paths must be non-empty list")
        elif path_theme_codes is not None:
            for path_code in paths:
                if path_code not in path_theme_codes:
                    errors.append(f"{prefix}: unknown compatible_paths entry {path_code!r}")

        stages = entry.get("compatible_stages")
        if not isinstance(stages, list) or not stages:
            errors.append(f"{prefix}: compatible_stages must be non-empty list")
        else:
            for stage in stages:
                if stage not in CANONICAL_STAGE_ORDER:
                    errors.append(f"{prefix}: unknown compatible_stages entry {stage!r}")

        signals = entry.get("produces_signals")
        if not isinstance(signals, list) or not signals:
            errors.append(f"{prefix}: produces_signals must be non-empty list")
        else:
            if len(signals) != len(set(signals)):
                errors.append(f"{prefix}: produces_signals must be unique")
            for sig in signals:
                if sig not in ALLOWED_PROGRESSION_SIGNAL_TYPES:
                    errors.append(f"{prefix}: unknown produces_signals entry {sig!r}")
                elif sig not in RITUAL_DEFINITION_ALLOWED_SIGNALS:
                    errors.append(
                        f"{prefix}: {sig!r} not allowed at ritual definition level "
                        "(use Habit/Goal/Cycle registries)"
                    )
            if "ritual_streak_confirmed" not in signals:
                errors.append(f"{prefix}: produces_signals must include ritual_streak_confirmed")

        if entry.get("difficulty_level") not in ALLOWED_DIFFICULTY_LEVELS:
            errors.append(f"{prefix}: invalid difficulty_level")

        if entry.get("status") not in ALLOWED_REGISTRY_STATUSES:
            errors.append(f"{prefix}: invalid status")

    return errors
