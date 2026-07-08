"""C1.6 — Validate Cycle Definition registry (temporal programs linking C1.1–C1.5)."""

from __future__ import annotations

import re
from typing import Any

from todayflow_backend.data.evolution_cd_validator import (
    ALLOWED_CYCLE_LENGTHS,
    ALLOWED_PROGRESSION_SIGNAL_TYPES,
    CANONICAL_STAGE_ORDER,
    FORBIDDEN_GATE_SIGNAL_PATTERN,
)

CYCLE_DEFINITION_REGISTRY_V1_CONTRACT = "cycle_definition_registry_v1"

ALLOWED_REGISTRY_STATUSES = frozenset({"draft", "active"})

ALLOWED_CYCLE_CATEGORIES = frozenset(
    {
        "discipline",
        "clarity",
        "purpose",
        "energy",
        "healing",
        "growth",
        "digital",
        "reflection",
    }
)

ALLOWED_COMPONENT_TYPES = frozenset({"practice", "habit", "goal", "ascetic", "ritual"})

ALLOWED_DIFFICULTY_LEVELS = frozenset({"beginner", "intermediate", "advanced"})

ALLOWED_COMPLETION_PERIODS = frozenset({"cycle"})

CYCLE_DEFINITION_ALLOWED_SIGNALS = frozenset({"cycle_completed"})

CANONICAL_CYCLE_DEFINITION_CODES: tuple[str, ...] = (
    "seven_day_energy_reset",
    "twenty_one_day_discipline_cycle",
    "twenty_one_day_reflection_cycle",
    "twenty_one_day_habit_building_cycle",
    "thirty_day_clarity_cycle",
    "thirty_day_purpose_arc",
    "ninety_day_architect_cycle",
    "twenty_one_day_digital_boundary_cycle",
)

FORBIDDEN_CYCLE_FIELD_NAMES = frozenset(
    {
        "frequency_type",
        "linked_practice_definition_code",
        "goal_type",
        "target_metric",
        "horizon",
        "ritual_category",
        "sequence_type",
        "instruction_text",
        "ui_text",
        "llm_prompt",
        "user_progress",
        "calendar_marks",
    }
)

FORBIDDEN_CYCLE_CONTENT_PATTERN = re.compile(
    r"(achievement|commerce|unlock|purchase|reward|badge|payment|subscription|llm.?prompt|ui.?card|variant.?text|instruction.?text)",
    re.I,
)

COMPONENT_V1_KEYS = frozenset(
    {
        "component_type",
        "component_code",
        "required",
        "minimum_required_for_completion",
    }
)

MINIMUM_COMPLETION_RULE_V1_KEYS = frozenset(
    {
        "minimum_active_days",
        "minimum_components_completed",
        "period",
    }
)

CYCLE_DEFINITION_V1_KEYS = frozenset(
    {
        "code",
        "title",
        "cycle_category",
        "description",
        "duration_days",
        "primary_path_theme",
        "components",
        "component_count",
        "minimum_completion_rule",
        "compatible_paths",
        "compatible_stages",
        "produces_signals",
        "difficulty_level",
        "status",
        "version",
    }
)

CYCLE_DEFINITION_REGISTRY_V1_TOP_KEYS = frozenset(
    {
        "contract_version",
        "domain",
        "version",
        "status",
        "description",
        "cycle_definitions",
    }
)


class CycleDefinitionRegistryValidationError(Exception):
    """Raised when cycle definition registry payload fails validation."""


def _scan_forbidden_content(value: str, prefix: str, errors: list[str]) -> None:
    if FORBIDDEN_CYCLE_CONTENT_PATTERN.search(value):
        errors.append(f"{prefix}: forbidden achievement/commerce/content marker in text")
    if FORBIDDEN_GATE_SIGNAL_PATTERN.search(value):
        errors.append(f"{prefix}: forbidden achievement/commerce marker in text")


def _validate_component(
    component: Any,
    *,
    prefix: str,
    practice_codes: frozenset[str] | None,
    habit_codes: frozenset[str] | None,
    goal_codes: frozenset[str] | None,
    ascetic_codes: frozenset[str] | None,
    ritual_codes: frozenset[str] | None,
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
        registry_map = {
            "practice": practice_codes,
            "habit": habit_codes,
            "goal": goal_codes,
            "ascetic": ascetic_codes,
            "ritual": ritual_codes,
        }
        codes = registry_map.get(comp_type if isinstance(comp_type, str) else "")
        if codes is not None and comp_code not in codes:
            errors.append(f"{prefix}: unknown {comp_type} component_code {comp_code!r}")
    else:
        errors.append(f"{prefix}: component_code must be string")

    if not isinstance(component.get("required"), bool):
        errors.append(f"{prefix}: required must be boolean")

    if not isinstance(component.get("minimum_required_for_completion"), bool):
        errors.append(f"{prefix}: minimum_required_for_completion must be boolean")


def validate_cycle_definition_registry_v1(
    payload: dict[str, Any],
    *,
    path_theme_codes: frozenset[str] | None = None,
    practice_codes: frozenset[str] | None = None,
    habit_codes: frozenset[str] | None = None,
    goal_codes: frozenset[str] | None = None,
    ascetic_codes: frozenset[str] | None = None,
    ritual_codes: frozenset[str] | None = None,
) -> list[str]:
    errors: list[str] = []

    if payload.get("contract_version") != CYCLE_DEFINITION_REGISTRY_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in CYCLE_DEFINITION_REGISTRY_V1_TOP_KEYS:
        if key not in payload:
            errors.append(f"missing top-level field: {key}")

    if payload.get("domain") != "practice":
        errors.append("domain must be practice")

    if payload.get("status") not in ALLOWED_REGISTRY_STATUSES:
        errors.append("invalid top-level status")

    definitions = payload.get("cycle_definitions")
    if not isinstance(definitions, dict):
        errors.append("cycle_definitions must be object")
        return errors

    expected_codes = set(CANONICAL_CYCLE_DEFINITION_CODES)
    if set(definitions.keys()) != expected_codes:
        missing = expected_codes - set(definitions.keys())
        extra = set(definitions.keys()) - expected_codes
        if missing:
            errors.append(f"missing cycle definitions: {sorted(missing)}")
        if extra:
            errors.append(f"unexpected cycle definitions: {sorted(extra)}")

    for code, entry in definitions.items():
        prefix = f"cycle_definition[{code}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: must be object")
            continue

        forbidden_present = set(entry.keys()) & FORBIDDEN_CYCLE_FIELD_NAMES
        if forbidden_present:
            errors.append(f"{prefix}: forbidden runtime/UI/content fields {sorted(forbidden_present)}")

        extra_keys = set(entry.keys()) - CYCLE_DEFINITION_V1_KEYS
        if extra_keys:
            errors.append(f"{prefix}: unexpected fields {sorted(extra_keys)}")

        for field in CYCLE_DEFINITION_V1_KEYS:
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

        if entry.get("cycle_category") not in ALLOWED_CYCLE_CATEGORIES:
            errors.append(f"{prefix}: invalid cycle_category")

        duration = entry.get("duration_days")
        if duration not in ALLOWED_CYCLE_LENGTHS:
            errors.append(f"{prefix}: duration_days must be one of 7, 21, 30, 90")

        primary_path = entry.get("primary_path_theme")
        if not isinstance(primary_path, str) or not primary_path.strip():
            errors.append(f"{prefix}: primary_path_theme must be non-empty string")
        elif path_theme_codes is not None and primary_path not in path_theme_codes:
            errors.append(f"{prefix}: unknown primary_path_theme {primary_path!r}")

        components = entry.get("components")
        component_count = entry.get("component_count")
        flagged_count = 0
        if not isinstance(components, list) or not components:
            errors.append(f"{prefix}: components must be non-empty list")
        elif not isinstance(component_count, int) or component_count < 1:
            errors.append(f"{prefix}: component_count must be positive int")
        elif len(components) != component_count:
            errors.append(f"{prefix}: component_count must match len(components)")
        else:
            for index, component in enumerate(components):
                comp_prefix = f"{prefix}.components[{index}]"
                _validate_component(
                    component,
                    prefix=comp_prefix,
                    practice_codes=practice_codes,
                    habit_codes=habit_codes,
                    goal_codes=goal_codes,
                    ascetic_codes=ascetic_codes,
                    ritual_codes=ritual_codes,
                    errors=errors,
                )
                if isinstance(component, dict) and component.get("minimum_required_for_completion") is True:
                    flagged_count += 1

        rule = entry.get("minimum_completion_rule")
        if not isinstance(rule, dict) or not rule:
            errors.append(f"{prefix}: minimum_completion_rule must be non-empty object")
        else:
            if set(rule.keys()) != MINIMUM_COMPLETION_RULE_V1_KEYS:
                errors.append(f"{prefix}: minimum_completion_rule has invalid keys")
            min_active = rule.get("minimum_active_days")
            if not isinstance(min_active, int) or min_active < 1:
                errors.append(f"{prefix}: minimum_completion_rule.minimum_active_days must be positive int")
            elif isinstance(duration, int) and min_active > duration:
                errors.append(f"{prefix}: minimum_active_days cannot exceed duration_days")
            min_components = rule.get("minimum_components_completed")
            if not isinstance(min_components, int) or min_components < 1:
                errors.append(f"{prefix}: minimum_completion_rule.minimum_components_completed must be positive int")
            if rule.get("period") != "cycle":
                errors.append(f"{prefix}: minimum_completion_rule.period must be cycle")
            if isinstance(components, list) and isinstance(min_components, int):
                if min_components > len(components):
                    errors.append(f"{prefix}: minimum_components_completed cannot exceed component_count")
                if flagged_count > 0 and min_components > flagged_count:
                    errors.append(
                        f"{prefix}: minimum_components_completed cannot exceed "
                        "minimum_required_for_completion count"
                    )

        paths = entry.get("compatible_paths")
        if not isinstance(paths, list) or not paths:
            errors.append(f"{prefix}: compatible_paths must be non-empty list")
        elif path_theme_codes is not None:
            for path_code in paths:
                if path_code not in path_theme_codes:
                    errors.append(f"{prefix}: unknown compatible_paths entry {path_code!r}")
            if isinstance(primary_path, str) and primary_path not in paths:
                errors.append(f"{prefix}: primary_path_theme must appear in compatible_paths")

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
                elif sig not in CYCLE_DEFINITION_ALLOWED_SIGNALS:
                    errors.append(
                        f"{prefix}: {sig!r} not allowed at cycle definition level "
                        "(component layers emit other signals)"
                    )
            if signals != ["cycle_completed"]:
                errors.append(f"{prefix}: produces_signals must be exactly ['cycle_completed']")

        if entry.get("difficulty_level") not in ALLOWED_DIFFICULTY_LEVELS:
            errors.append(f"{prefix}: invalid difficulty_level")

        if entry.get("status") not in ALLOWED_REGISTRY_STATUSES:
            errors.append(f"{prefix}: invalid status")

    return errors
