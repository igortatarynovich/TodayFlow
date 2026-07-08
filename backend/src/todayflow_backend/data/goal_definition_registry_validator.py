"""C1.3 — Validate Goal Definition registry (desired outcomes, not actions)."""

from __future__ import annotations

import re
from typing import Any

from todayflow_backend.data.evolution_cd_validator import (
    ALLOWED_PROGRESSION_SIGNAL_TYPES,
    CANONICAL_STAGE_ORDER,
    FORBIDDEN_GATE_SIGNAL_PATTERN,
)

GOAL_DEFINITION_REGISTRY_V1_CONTRACT = "goal_definition_registry_v1"

ALLOWED_REGISTRY_STATUSES = frozenset({"draft", "active"})

ALLOWED_GOAL_TYPES = frozenset({"weekly", "milestone", "long_horizon"})

ALLOWED_GOAL_CATEGORIES = frozenset(
    {
        "clarity",
        "discipline",
        "purpose",
        "relationships",
        "body",
        "energy",
        "growth",
        "wellbeing",
        "focus",
    }
)

ALLOWED_GOAL_HORIZONS = frozenset({"week", "month", "quarter", "year", "open_ended"})

ALLOWED_DIFFICULTY_LEVELS = frozenset({"beginner", "intermediate", "advanced"})

ALLOWED_METRIC_TYPES = frozenset(
    {
        "active_days",
        "sessions_completed",
        "theme_closed",
        "intention_set",
        "review_completed",
        "habit_streak_days",
        "milestone_reached",
    }
)

ALLOWED_METRIC_UNITS = frozenset({"days", "weeks", "months", "sessions", "count", "percent"})

GOAL_DEFINITION_ALLOWED_SIGNALS = frozenset(
    {
        "goal_milestone_reached",
        "weekly_goal_completed",
    }
)

CANONICAL_GOAL_DEFINITION_CODES: tuple[str, ...] = (
    "weekly_clarity_theme",
    "weekly_discipline_rhythm",
    "weekly_reflection_closure",
    "habit_consistency_milestone",
    "purpose_direction_milestone",
    "relationship_focus_week",
    "body_restoration_milestone",
    "focus_sprint_week",
    "architect_system_review",
    "energy_balance_week",
)

FORBIDDEN_GOAL_CONTENT_PATTERN = re.compile(
    r"(achievement|commerce|unlock|purchase|reward|badge|payment|subscription|llm.?prompt|ui.?card|variant.?text|instruction.?text)",
    re.I,
)

GOAL_DEFINITION_V1_KEYS = frozenset(
    {
        "code",
        "title",
        "goal_type",
        "goal_category",
        "description",
        "target_metric",
        "horizon",
        "compatible_paths",
        "compatible_stages",
        "produces_signals",
        "difficulty_level",
        "status",
        "version",
    }
)

TARGET_METRIC_V1_KEYS = frozenset(
    {
        "metric_type",
        "target_value",
        "unit",
    }
)

GOAL_DEFINITION_REGISTRY_V1_TOP_KEYS = frozenset(
    {
        "contract_version",
        "domain",
        "version",
        "status",
        "description",
        "goal_definitions",
    }
)

GOAL_TYPE_TO_HORIZON: dict[str, frozenset[str]] = {
    "weekly": frozenset({"week"}),
    "milestone": frozenset({"week", "month", "quarter"}),
    "long_horizon": frozenset({"quarter", "year", "open_ended"}),
}

GOAL_TYPE_REQUIRED_SIGNALS: dict[str, frozenset[str]] = {
    "weekly": frozenset({"weekly_goal_completed"}),
    "milestone": frozenset({"goal_milestone_reached"}),
    "long_horizon": frozenset({"goal_milestone_reached"}),
}


class GoalDefinitionRegistryValidationError(Exception):
    """Raised when goal definition registry payload fails validation."""


def _scan_forbidden_content(value: str, prefix: str, errors: list[str]) -> None:
    if FORBIDDEN_GOAL_CONTENT_PATTERN.search(value):
        errors.append(f"{prefix}: forbidden achievement/commerce/content marker in text")
    if FORBIDDEN_GATE_SIGNAL_PATTERN.search(value):
        errors.append(f"{prefix}: forbidden achievement/commerce marker in text")


def validate_goal_definition_registry_v1(
    payload: dict[str, Any],
    *,
    path_theme_codes: frozenset[str] | None = None,
) -> list[str]:
    errors: list[str] = []

    if payload.get("contract_version") != GOAL_DEFINITION_REGISTRY_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in GOAL_DEFINITION_REGISTRY_V1_TOP_KEYS:
        if key not in payload:
            errors.append(f"missing top-level field: {key}")

    if payload.get("domain") != "practice":
        errors.append("domain must be practice")

    if payload.get("status") not in ALLOWED_REGISTRY_STATUSES:
        errors.append("invalid top-level status")

    definitions = payload.get("goal_definitions")
    if not isinstance(definitions, dict):
        errors.append("goal_definitions must be object")
        return errors

    expected_codes = set(CANONICAL_GOAL_DEFINITION_CODES)
    if set(definitions.keys()) != expected_codes:
        missing = expected_codes - set(definitions.keys())
        extra = set(definitions.keys()) - expected_codes
        if missing:
            errors.append(f"missing goal definitions: {sorted(missing)}")
        if extra:
            errors.append(f"unexpected goal definitions: {sorted(extra)}")

    for code, entry in definitions.items():
        prefix = f"goal_definition[{code}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: must be object")
            continue

        extra_keys = set(entry.keys()) - GOAL_DEFINITION_V1_KEYS
        if extra_keys:
            errors.append(f"{prefix}: unexpected fields {sorted(extra_keys)}")

        for field in GOAL_DEFINITION_V1_KEYS:
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

        goal_type = entry.get("goal_type")
        if goal_type not in ALLOWED_GOAL_TYPES:
            errors.append(f"{prefix}: invalid goal_type")

        if entry.get("goal_category") not in ALLOWED_GOAL_CATEGORIES:
            errors.append(f"{prefix}: invalid goal_category")

        horizon = entry.get("horizon")
        if horizon not in ALLOWED_GOAL_HORIZONS:
            errors.append(f"{prefix}: invalid horizon")
        elif isinstance(goal_type, str) and horizon not in GOAL_TYPE_TO_HORIZON.get(goal_type, frozenset()):
            errors.append(f"{prefix}: horizon {horizon!r} incompatible with goal_type {goal_type!r}")

        metric = entry.get("target_metric")
        if not isinstance(metric, dict) or not metric:
            errors.append(f"{prefix}: target_metric must be non-empty object")
        else:
            if set(metric.keys()) != TARGET_METRIC_V1_KEYS:
                errors.append(f"{prefix}: target_metric has invalid keys")
            if metric.get("metric_type") not in ALLOWED_METRIC_TYPES:
                errors.append(f"{prefix}: target_metric.metric_type invalid")
            target_value = metric.get("target_value")
            if not isinstance(target_value, int) or target_value < 1:
                errors.append(f"{prefix}: target_metric.target_value must be positive int")
            if metric.get("unit") not in ALLOWED_METRIC_UNITS:
                errors.append(f"{prefix}: target_metric.unit invalid")

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
                elif sig not in GOAL_DEFINITION_ALLOWED_SIGNALS:
                    errors.append(
                        f"{prefix}: {sig!r} not allowed at goal definition level "
                        "(use Practice/Habit/Ritual/Cycle registries)"
                    )
            if isinstance(goal_type, str):
                required = GOAL_TYPE_REQUIRED_SIGNALS.get(goal_type, frozenset())
                missing_signals = required - set(signals)
                if missing_signals:
                    errors.append(
                        f"{prefix}: produces_signals must include {sorted(missing_signals)} for goal_type {goal_type!r}"
                    )

        if entry.get("difficulty_level") not in ALLOWED_DIFFICULTY_LEVELS:
            errors.append(f"{prefix}: invalid difficulty_level")

        if entry.get("status") not in ALLOWED_REGISTRY_STATUSES:
            errors.append(f"{prefix}: invalid status")

    return errors
