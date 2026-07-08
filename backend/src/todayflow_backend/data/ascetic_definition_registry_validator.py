"""C1.4 — Validate Ascetic Definition registry (restrictions, not habits or goals)."""

from __future__ import annotations

import re
from typing import Any

from todayflow_backend.data.evolution_cd_validator import (
    ALLOWED_PROGRESSION_SIGNAL_TYPES,
    CANONICAL_STAGE_ORDER,
    FORBIDDEN_GATE_SIGNAL_PATTERN,
)

ASCETIC_DEFINITION_REGISTRY_V1_CONTRACT = "ascetic_definition_registry_v1"

ALLOWED_REGISTRY_STATUSES = frozenset({"draft", "active"})

ALLOWED_ASCETIC_CATEGORIES = frozenset(
    {
        "digital",
        "food",
        "spending",
        "speech",
        "sleep",
        "discipline",
        "emotional",
    }
)

ASCETIC_CATEGORIES_REQUIRING_SAFETY_NOTE = frozenset(
    {
        "food",
        "sleep",
        "emotional",
        "discipline",
    }
)

ALLOWED_RESTRICTION_TYPES = frozenset({"abstain", "limit", "time_window", "replacement"})

ALLOWED_SUGGESTED_DURATION_DAYS = frozenset({7, 21, 30, 90})

ALLOWED_DIFFICULTY_LEVELS = frozenset({"beginner", "intermediate", "advanced"})

ALLOWED_FAILURE_TOLERANCE = frozenset({"strict", "flexible"})

ALLOWED_COMPLIANCE_TYPES = frozenset(
    {
        "daily_abstain",
        "daily_limit",
        "time_window_hold",
        "replacement_used",
    }
)

ALLOWED_SUCCESS_PERIODS = frozenset({"day"})

ASCETIC_POTENTIAL_SIGNAL_TYPES = frozenset({"practice_completed"})

FORBIDDEN_ASCETIC_FIELD_NAMES = frozenset(
    {
        "linked_practice_definition_code",
        "linked_habit_definition_code",
        "frequency_type",
        "goal_type",
        "target_metric",
        "horizon",
        "minimum_completion_rule",
        "instruction_text",
        "ui_text",
        "llm_prompt",
    }
)

CANONICAL_ASCETIC_DEFINITION_CODES: tuple[str, ...] = (
    "no_social_media_evening",
    "no_sugar",
    "no_impulse_spending",
    "no_complaining",
    "early_sleep_window",
    "morning_no_phone",
    "mindful_speech",
    "no_alcohol_period",
    "no_multitasking",
    "no_late_night_scrolling",
)

FORBIDDEN_ASCETIC_CONTENT_PATTERN = re.compile(
    r"(achievement|commerce|unlock|purchase|reward|badge|payment|subscription|llm.?prompt|ui.?card|variant.?text|instruction.?text|medical.?advice|clinical.?recommendation)",
    re.I,
)

ASCETIC_DEFINITION_V1_KEYS = frozenset(
    {
        "code",
        "title",
        "ascetic_category",
        "description",
        "restriction_type",
        "compatible_paths",
        "compatible_stages",
        "suggested_duration_days",
        "minimum_success_rule",
        "failure_tolerance",
        "requires_safety_note",
        "contraindications",
        "produces_signals",
        "potential_signal_types",
        "difficulty_level",
        "status",
        "version",
    }
)

MINIMUM_SUCCESS_RULE_V1_KEYS = frozenset(
    {
        "compliance_type",
        "minimum_compliant_days",
        "period",
    }
)

ASCETIC_DEFINITION_REGISTRY_V1_TOP_KEYS = frozenset(
    {
        "contract_version",
        "domain",
        "version",
        "status",
        "description",
        "ascetic_definitions",
    }
)


class AsceticDefinitionRegistryValidationError(Exception):
    """Raised when ascetic definition registry payload fails validation."""


def _scan_forbidden_content(value: str, prefix: str, errors: list[str]) -> None:
    if FORBIDDEN_ASCETIC_CONTENT_PATTERN.search(value):
        errors.append(f"{prefix}: forbidden achievement/commerce/medical-content marker in text")
    if FORBIDDEN_GATE_SIGNAL_PATTERN.search(value):
        errors.append(f"{prefix}: forbidden achievement/commerce marker in text")


def validate_ascetic_definition_registry_v1(
    payload: dict[str, Any],
    *,
    path_theme_codes: frozenset[str] | None = None,
) -> list[str]:
    errors: list[str] = []

    if payload.get("contract_version") != ASCETIC_DEFINITION_REGISTRY_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in ASCETIC_DEFINITION_REGISTRY_V1_TOP_KEYS:
        if key not in payload:
            errors.append(f"missing top-level field: {key}")

    if payload.get("domain") != "practice":
        errors.append("domain must be practice")

    if payload.get("status") not in ALLOWED_REGISTRY_STATUSES:
        errors.append("invalid top-level status")

    definitions = payload.get("ascetic_definitions")
    if not isinstance(definitions, dict):
        errors.append("ascetic_definitions must be object")
        return errors

    expected_codes = set(CANONICAL_ASCETIC_DEFINITION_CODES)
    if set(definitions.keys()) != expected_codes:
        missing = expected_codes - set(definitions.keys())
        extra = set(definitions.keys()) - expected_codes
        if missing:
            errors.append(f"missing ascetic definitions: {sorted(missing)}")
        if extra:
            errors.append(f"unexpected ascetic definitions: {sorted(extra)}")

    for code, entry in definitions.items():
        prefix = f"ascetic_definition[{code}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: must be object")
            continue

        forbidden_present = set(entry.keys()) & FORBIDDEN_ASCETIC_FIELD_NAMES
        if forbidden_present:
            errors.append(f"{prefix}: forbidden habit/goal/practice fields {sorted(forbidden_present)}")

        extra_keys = set(entry.keys()) - ASCETIC_DEFINITION_V1_KEYS
        if extra_keys:
            errors.append(f"{prefix}: unexpected fields {sorted(extra_keys)}")

        for field in ASCETIC_DEFINITION_V1_KEYS:
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

        category = entry.get("ascetic_category")
        if category not in ALLOWED_ASCETIC_CATEGORIES:
            errors.append(f"{prefix}: invalid ascetic_category")

        if entry.get("restriction_type") not in ALLOWED_RESTRICTION_TYPES:
            errors.append(f"{prefix}: invalid restriction_type")

        duration = entry.get("suggested_duration_days")
        if duration not in ALLOWED_SUGGESTED_DURATION_DAYS:
            errors.append(f"{prefix}: suggested_duration_days must be one of 7, 21, 30, 90")

        rule = entry.get("minimum_success_rule")
        if not isinstance(rule, dict) or not rule:
            errors.append(f"{prefix}: minimum_success_rule must be non-empty object")
        else:
            if set(rule.keys()) != MINIMUM_SUCCESS_RULE_V1_KEYS:
                errors.append(f"{prefix}: minimum_success_rule has invalid keys")
            if rule.get("compliance_type") not in ALLOWED_COMPLIANCE_TYPES:
                errors.append(f"{prefix}: minimum_success_rule.compliance_type invalid")
            min_days = rule.get("minimum_compliant_days")
            if not isinstance(min_days, int) or min_days < 1:
                errors.append(f"{prefix}: minimum_success_rule.minimum_compliant_days must be positive int")
            if rule.get("period") not in ALLOWED_SUCCESS_PERIODS:
                errors.append(f"{prefix}: minimum_success_rule.period invalid")

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
        if not isinstance(signals, list):
            errors.append(f"{prefix}: produces_signals must be list")
        elif signals:
            errors.append(f"{prefix}: produces_signals must be empty at CD level (runtime emits signals)")

        potential = entry.get("potential_signal_types")
        if not isinstance(potential, list):
            errors.append(f"{prefix}: potential_signal_types must be list")
        else:
            if len(potential) != len(set(potential)):
                errors.append(f"{prefix}: potential_signal_types must be unique")
            for sig in potential:
                if sig not in ALLOWED_PROGRESSION_SIGNAL_TYPES:
                    errors.append(f"{prefix}: unknown potential_signal_types entry {sig!r}")
                elif sig not in ASCETIC_POTENTIAL_SIGNAL_TYPES:
                    errors.append(
                        f"{prefix}: {sig!r} not allowed as ascetic potential signal "
                        "(ritual/cycle/habit/goal signals belong to other layers)"
                    )

        requires_safety = entry.get("requires_safety_note")
        if not isinstance(requires_safety, bool):
            errors.append(f"{prefix}: requires_safety_note must be boolean")
        elif category in ASCETIC_CATEGORIES_REQUIRING_SAFETY_NOTE and requires_safety is not True:
            errors.append(f"{prefix}: requires_safety_note must be true for category {category!r}")

        contraindications = entry.get("contraindications")
        if not isinstance(contraindications, list):
            errors.append(f"{prefix}: contraindications must be list")
        elif category in ASCETIC_CATEGORIES_REQUIRING_SAFETY_NOTE and not contraindications:
            errors.append(f"{prefix}: contraindications required when requires_safety_note applies")

        if entry.get("failure_tolerance") not in ALLOWED_FAILURE_TOLERANCE:
            errors.append(f"{prefix}: invalid failure_tolerance")

        if entry.get("difficulty_level") not in ALLOWED_DIFFICULTY_LEVELS:
            errors.append(f"{prefix}: invalid difficulty_level")

        if entry.get("status") not in ALLOWED_REGISTRY_STATUSES:
            errors.append(f"{prefix}: invalid status")

    return errors
