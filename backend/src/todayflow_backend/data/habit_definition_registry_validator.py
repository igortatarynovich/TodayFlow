"""C1.2 — Validate Habit Definition registry (recurrence patterns linked to C1.1)."""

from __future__ import annotations

import re
from typing import Any

from todayflow_backend.data.evolution_cd_validator import (
    ALLOWED_PROGRESSION_SIGNAL_TYPES,
    CANONICAL_STAGE_ORDER,
    FORBIDDEN_GATE_SIGNAL_PATTERN,
)

HABIT_DEFINITION_REGISTRY_V1_CONTRACT = "habit_definition_registry_v1"

ALLOWED_REGISTRY_STATUSES = frozenset({"draft", "active"})

ALLOWED_HABIT_CATEGORIES = frozenset(
    {
        "wellness",
        "focus",
        "reflection",
        "discipline",
        "body",
        "planning",
    }
)

ALLOWED_FREQUENCY_TYPES = frozenset({"daily", "weekly", "custom"})

ALLOWED_DIFFICULTY_LEVELS = frozenset({"beginner", "intermediate", "advanced"})

ALLOWED_FAILURE_TOLERANCE = frozenset({"strict", "flexible"})

ALLOWED_COMPLETION_PERIODS = frozenset({"day", "week"})

HABIT_DEFINITION_ALLOWED_SIGNALS = frozenset(
    {
        "practice_completed",
        "habit_streak_confirmed",
    }
)

CANONICAL_HABIT_DEFINITION_CODES: tuple[str, ...] = (
    "daily_breathing",
    "evening_reflection",
    "morning_planning",
    "daily_gratitude",
    "body_activation",
    "attention_training",
    "meditation_minutes",
    "self_observation_check",
    "journaling_streak",
    "visualization_practice",
)

FORBIDDEN_HABIT_CONTENT_PATTERN = re.compile(
    r"(achievement|commerce|unlock|purchase|reward|badge|payment|subscription|llm.?prompt|ui.?card|variant.?text|instruction.?text)",
    re.I,
)

HABIT_DEFINITION_V1_KEYS = frozenset(
    {
        "code",
        "title",
        "linked_practice_definition_code",
        "habit_category",
        "frequency_type",
        "minimum_completion_rule",
        "recommended_duration_range",
        "compatible_paths",
        "compatible_stages",
        "produces_signals",
        "difficulty_level",
        "failure_tolerance",
        "status",
        "version",
    }
)

MINIMUM_COMPLETION_RULE_V1_KEYS = frozenset(
    {
        "sessions_required",
        "period",
        "minimum_duration_minutes",
    }
)

DURATION_RANGE_V1_KEYS = frozenset({"min_minutes", "max_minutes"})

HABIT_DEFINITION_REGISTRY_V1_TOP_KEYS = frozenset(
    {
        "contract_version",
        "domain",
        "version",
        "status",
        "description",
        "habit_definitions",
    }
)


class HabitDefinitionRegistryValidationError(Exception):
    """Raised when habit definition registry payload fails validation."""


def _scan_forbidden_content(value: str, prefix: str, errors: list[str]) -> None:
    if FORBIDDEN_HABIT_CONTENT_PATTERN.search(value):
        errors.append(f"{prefix}: forbidden achievement/commerce/content marker in text")
    if FORBIDDEN_GATE_SIGNAL_PATTERN.search(value):
        errors.append(f"{prefix}: forbidden achievement/commerce marker in text")


def validate_habit_definition_registry_v1(
    payload: dict[str, Any],
    *,
    path_theme_codes: frozenset[str] | None = None,
    practice_definition_codes: frozenset[str] | None = None,
) -> list[str]:
    errors: list[str] = []

    if payload.get("contract_version") != HABIT_DEFINITION_REGISTRY_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in HABIT_DEFINITION_REGISTRY_V1_TOP_KEYS:
        if key not in payload:
            errors.append(f"missing top-level field: {key}")

    if payload.get("domain") != "practice":
        errors.append("domain must be practice")

    if payload.get("status") not in ALLOWED_REGISTRY_STATUSES:
        errors.append("invalid top-level status")

    definitions = payload.get("habit_definitions")
    if not isinstance(definitions, dict):
        errors.append("habit_definitions must be object")
        return errors

    expected_codes = set(CANONICAL_HABIT_DEFINITION_CODES)
    if set(definitions.keys()) != expected_codes:
        missing = expected_codes - set(definitions.keys())
        extra = set(definitions.keys()) - expected_codes
        if missing:
            errors.append(f"missing habit definitions: {sorted(missing)}")
        if extra:
            errors.append(f"unexpected habit definitions: {sorted(extra)}")

    for code, entry in definitions.items():
        prefix = f"habit_definition[{code}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: must be object")
            continue

        extra_keys = set(entry.keys()) - HABIT_DEFINITION_V1_KEYS
        if extra_keys:
            errors.append(f"{prefix}: unexpected fields {sorted(extra_keys)}")

        for field in HABIT_DEFINITION_V1_KEYS:
            if field not in entry:
                errors.append(f"{prefix}: missing field {field!r}")

        if entry.get("code") != code:
            errors.append(f"{prefix}: code mismatch")

        title = entry.get("title")
        if isinstance(title, str):
            _scan_forbidden_content(title, prefix, errors)
        else:
            errors.append(f"{prefix}: title must be string")

        linked = entry.get("linked_practice_definition_code")
        if not isinstance(linked, str) or not linked.strip():
            errors.append(f"{prefix}: linked_practice_definition_code must be non-empty string")
        elif practice_definition_codes is not None and linked not in practice_definition_codes:
            errors.append(f"{prefix}: unknown linked_practice_definition_code {linked!r}")

        if entry.get("habit_category") not in ALLOWED_HABIT_CATEGORIES:
            errors.append(f"{prefix}: invalid habit_category")

        frequency = entry.get("frequency_type")
        if frequency not in ALLOWED_FREQUENCY_TYPES:
            errors.append(f"{prefix}: invalid frequency_type")

        rule = entry.get("minimum_completion_rule")
        if not isinstance(rule, dict) or not rule:
            errors.append(f"{prefix}: minimum_completion_rule must be non-empty object")
        else:
            if set(rule.keys()) != MINIMUM_COMPLETION_RULE_V1_KEYS:
                errors.append(f"{prefix}: minimum_completion_rule has invalid keys")
            sessions = rule.get("sessions_required")
            if not isinstance(sessions, int) or sessions < 1:
                errors.append(f"{prefix}: minimum_completion_rule.sessions_required must be positive int")
            period = rule.get("period")
            if period not in ALLOWED_COMPLETION_PERIODS:
                errors.append(f"{prefix}: minimum_completion_rule.period invalid")
            min_dur = rule.get("minimum_duration_minutes")
            if not isinstance(min_dur, int) or min_dur < 1:
                errors.append(f"{prefix}: minimum_completion_rule.minimum_duration_minutes must be positive int")
            if frequency == "daily" and period != "day":
                errors.append(f"{prefix}: daily habit must use period day in minimum_completion_rule")
            if frequency == "weekly" and period != "week":
                errors.append(f"{prefix}: weekly habit must use period week in minimum_completion_rule")

        duration = entry.get("recommended_duration_range")
        if not isinstance(duration, dict):
            errors.append(f"{prefix}: recommended_duration_range must be object")
        else:
            if set(duration.keys()) != DURATION_RANGE_V1_KEYS:
                errors.append(f"{prefix}: recommended_duration_range must have min_minutes and max_minutes")
            min_m = duration.get("min_minutes")
            max_m = duration.get("max_minutes")
            if not isinstance(min_m, int) or min_m < 1:
                errors.append(f"{prefix}: recommended_duration_range.min_minutes must be positive int")
            if not isinstance(max_m, int) or max_m < 1:
                errors.append(f"{prefix}: recommended_duration_range.max_minutes must be positive int")
            if isinstance(min_m, int) and isinstance(max_m, int) and min_m > max_m:
                errors.append(f"{prefix}: recommended_duration_range min must be <= max")

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
                elif sig not in HABIT_DEFINITION_ALLOWED_SIGNALS:
                    errors.append(
                        f"{prefix}: {sig!r} not allowed at habit definition level "
                        "(use Ritual/Goal/Cycle registries)"
                    )
            if "habit_streak_confirmed" not in signals:
                errors.append(f"{prefix}: produces_signals must include habit_streak_confirmed")

        if entry.get("difficulty_level") not in ALLOWED_DIFFICULTY_LEVELS:
            errors.append(f"{prefix}: invalid difficulty_level")

        if entry.get("failure_tolerance") not in ALLOWED_FAILURE_TOLERANCE:
            errors.append(f"{prefix}: invalid failure_tolerance")

        if entry.get("status") not in ALLOWED_REGISTRY_STATUSES:
            errors.append(f"{prefix}: invalid status")

    return errors
