"""C1.1 — Validate Practice Definition registry (action types, not content)."""

from __future__ import annotations

from typing import Any

from todayflow_backend.data.evolution_cd_validator import (
    ALLOWED_PROGRESSION_SIGNAL_TYPES,
    CANONICAL_STAGE_ORDER,
)

PRACTICE_DEFINITION_REGISTRY_V1_CONTRACT = "practice_definition_registry_v1"

ALLOWED_REGISTRY_STATUSES = frozenset({"draft", "active"})

ALLOWED_LEVELS = frozenset({"low", "medium", "high"})

CANONICAL_PRACTICE_CATEGORIES: tuple[str, ...] = (
    "breathing",
    "journaling",
    "reflection",
    "meditation",
    "visualization",
    "body_activation",
    "gratitude",
    "attention_training",
    "planning",
    "self_observation",
)

# Practice definitions may only declare practice-level signals (not habit/ritual/cycle/goal).
PRACTICE_DEFINITION_ALLOWED_SIGNALS = frozenset(
    {
        "practice_completed",
        "evening_reflection_confirmed",
    }
)

PRACTICE_DEFINITION_V1_KEYS = frozenset(
    {
        "code",
        "category",
        "title",
        "description",
        "effort_level",
        "reflection_level",
        "duration_range",
        "compatible_paths",
        "compatible_stages",
        "produces_signals",
        "contraindications",
        "status",
        "version",
    }
)

DURATION_RANGE_V1_KEYS = frozenset({"min_minutes", "max_minutes"})

PRACTICE_DEFINITION_REGISTRY_V1_TOP_KEYS = frozenset(
    {
        "contract_version",
        "domain",
        "version",
        "status",
        "description",
        "practice_definitions",
    }
)


class PracticeDefinitionRegistryValidationError(Exception):
    """Raised when practice definition registry payload fails validation."""


def validate_practice_definition_registry_v1(
    payload: dict[str, Any],
    *,
    path_theme_codes: frozenset[str] | None = None,
) -> list[str]:
    errors: list[str] = []

    if payload.get("contract_version") != PRACTICE_DEFINITION_REGISTRY_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in PRACTICE_DEFINITION_REGISTRY_V1_TOP_KEYS:
        if key not in payload:
            errors.append(f"missing top-level field: {key}")

    if payload.get("domain") != "practice":
        errors.append("domain must be practice")

    if payload.get("status") not in ALLOWED_REGISTRY_STATUSES:
        errors.append("invalid top-level status")

    definitions = payload.get("practice_definitions")
    if not isinstance(definitions, dict):
        errors.append("practice_definitions must be object")
        return errors

    expected_codes = set(CANONICAL_PRACTICE_CATEGORIES)
    if set(definitions.keys()) != expected_codes:
        missing = expected_codes - set(definitions.keys())
        extra = set(definitions.keys()) - expected_codes
        if missing:
            errors.append(f"missing practice definitions: {sorted(missing)}")
        if extra:
            errors.append(f"unexpected practice definitions: {sorted(extra)}")

    for code, entry in definitions.items():
        prefix = f"practice_definition[{code}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: must be object")
            continue

        for field in PRACTICE_DEFINITION_V1_KEYS:
            if field not in entry:
                errors.append(f"{prefix}: missing field {field!r}")

        if entry.get("code") != code:
            errors.append(f"{prefix}: code mismatch")

        category = entry.get("category")
        if category not in CANONICAL_PRACTICE_CATEGORIES:
            errors.append(f"{prefix}: invalid category")

        if entry.get("effort_level") not in ALLOWED_LEVELS:
            errors.append(f"{prefix}: invalid effort_level")

        if entry.get("reflection_level") not in ALLOWED_LEVELS:
            errors.append(f"{prefix}: invalid reflection_level")

        duration = entry.get("duration_range")
        if not isinstance(duration, dict):
            errors.append(f"{prefix}: duration_range must be object")
        else:
            if set(duration.keys()) != DURATION_RANGE_V1_KEYS:
                errors.append(f"{prefix}: duration_range must have min_minutes and max_minutes")
            min_m = duration.get("min_minutes")
            max_m = duration.get("max_minutes")
            if not isinstance(min_m, int) or min_m < 1:
                errors.append(f"{prefix}: duration_range.min_minutes must be positive int")
            if not isinstance(max_m, int) or max_m < 1:
                errors.append(f"{prefix}: duration_range.max_minutes must be positive int")
            if isinstance(min_m, int) and isinstance(max_m, int) and min_m > max_m:
                errors.append(f"{prefix}: duration_range min must be <= max")

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
                elif sig not in PRACTICE_DEFINITION_ALLOWED_SIGNALS:
                    errors.append(
                        f"{prefix}: {sig!r} not allowed at practice definition level "
                        "(use Habit/Ritual/Goal/Cycle registries)"
                    )

        contraindications = entry.get("contraindications")
        if not isinstance(contraindications, list):
            errors.append(f"{prefix}: contraindications must be list")
        elif any(not isinstance(item, str) or not item.strip() for item in contraindications):
            errors.append(f"{prefix}: contraindications entries must be non-empty strings")

        if entry.get("status") not in ALLOWED_REGISTRY_STATUSES:
            errors.append(f"{prefix}: invalid status")

        if "practice_completed" not in (signals or []):
            errors.append(f"{prefix}: produces_signals must include practice_completed")

    return errors
