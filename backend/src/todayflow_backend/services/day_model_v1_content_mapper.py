"""P1.2 — Map day_model_interpretation_v1 to Content Contract lookup keys (no prose/LLM)."""

from __future__ import annotations

from typing import Any

from todayflow_backend.data.day_content_registry_loader import (
    load_day_content_registry,
    registry_has_key,
)
from todayflow_backend.services.day_model_v1_interpreter import (
    ACTION_MODE_VALUES,
    DAY_MODEL_INTERPRETATION_V1_CONTRACT,
    OPPORTUNITY_CLASS_VALUES,
    PRESSURE_LEVEL_VALUES,
    RISK_CLASS_VALUES,
    STRATEGY_VALUES,
    TEMPO_INSTRUCTION_VALUES,
    REFLECTION_MODE_VALUES,
)

DAY_MODEL_CONTENT_MAPPING_V1_CONTRACT = "day_model_content_mapping_v1"

INTERPRETATION_FIELD_PREFIXES = {
    "strategy": "day.strategy",
    "opportunity_class": "day.opportunity",
    "risk_class": "day.risk",
    "tempo_instruction": "day.tempo",
    "action_mode": "day.action_mode",
    "reflection_mode": "day.reflection",
    "pressure_level": "day.pressure",
}

INTERPRETATION_FIELD_ALLOWED = {
    "strategy": STRATEGY_VALUES,
    "opportunity_class": OPPORTUNITY_CLASS_VALUES,
    "risk_class": RISK_CLASS_VALUES,
    "tempo_instruction": TEMPO_INSTRUCTION_VALUES,
    "action_mode": ACTION_MODE_VALUES,
    "reflection_mode": REFLECTION_MODE_VALUES,
    "pressure_level": PRESSURE_LEVEL_VALUES,
}

CONTENT_SLOT_NAMES = frozenset(
    {
        "headline",
        "guidance",
        "risk_warning",
        "action_hint",
        "reflection_hint",
        "tempo_hint",
    }
)

DAY_MODEL_CONTENT_MAPPING_V1_KEYS = frozenset(
    {
        "contract_version",
        "content_keys",
        "required_slots",
        "optional_slots",
        "missing_keys",
        "degraded",
    }
)

DEGRADED_FALLBACK_KEY = "day.mapping.degraded"


class DayModelContentMappingError(ValueError):
    """Raised when input is not a valid day_model_interpretation_v1 payload."""


def _require_interpretation(interpretation: dict[str, Any]) -> None:
    if interpretation.get("contract_version") != DAY_MODEL_INTERPRETATION_V1_CONTRACT:
        raise DayModelContentMappingError(
            f"expected contract_version={DAY_MODEL_INTERPRETATION_V1_CONTRACT!r}, "
            f"got {interpretation.get('contract_version')!r}"
        )
    for field in INTERPRETATION_FIELD_PREFIXES:
        if field not in interpretation:
            raise DayModelContentMappingError(f"missing interpretation field: {field}")


def _content_key_for_field(field: str, value: str) -> str:
    prefix = INTERPRETATION_FIELD_PREFIXES[field]
    return f"{prefix}.{value}"


def _build_content_keys(interpretation: dict[str, Any]) -> dict[str, str]:
    return {
        field: _content_key_for_field(field, str(interpretation[field]))
        for field in INTERPRETATION_FIELD_PREFIXES
    }


def _resolve_missing_keys(
    content_keys: dict[str, str],
    registry: dict[str, Any],
) -> list[str]:
    missing: list[str] = []
    for key in content_keys.values():
        if not registry_has_key(key, registry):
            missing.append(key)
    return sorted(set(missing))


def _build_required_slots(content_keys: dict[str, str]) -> dict[str, list[str]]:
    return {
        "headline": [content_keys["strategy"]],
        "guidance": [
            content_keys["strategy"],
            content_keys["opportunity_class"],
            content_keys["pressure_level"],
        ],
        "risk_warning": [content_keys["risk_class"]],
        "action_hint": [content_keys["action_mode"]],
        "tempo_hint": [content_keys["tempo_instruction"]],
    }


def _build_optional_slots(
    content_keys: dict[str, str],
    interpretation: dict[str, Any],
    *,
    degraded: bool,
) -> dict[str, list[str]]:
    optional: dict[str, list[str]] = {}
    if interpretation["reflection_mode"] != "none":
        optional["reflection_hint"] = [content_keys["reflection_mode"]]
    if degraded:
        optional["headline"] = [DEGRADED_FALLBACK_KEY]
    return optional


def map_day_model_interpretation_to_content_keys(
    interpretation: dict[str, Any],
    *,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    P1.2 — resolve Content Contract lookup keys and slot assignments.

    Input: only day_model_interpretation_v1. Output: keys and slots — no prose, no LLM.
    """
    _require_interpretation(interpretation)
    reg = registry if registry is not None else load_day_content_registry()

    content_keys = _build_content_keys(interpretation)
    missing_keys = _resolve_missing_keys(content_keys, reg)
    degraded = bool(interpretation.get("degraded", False)) or bool(missing_keys)

    required_slots = _build_required_slots(content_keys)
    optional_slots = _build_optional_slots(content_keys, interpretation, degraded=degraded)

    return {
        "contract_version": DAY_MODEL_CONTENT_MAPPING_V1_CONTRACT,
        "content_keys": content_keys,
        "required_slots": required_slots,
        "optional_slots": optional_slots,
        "missing_keys": missing_keys,
        "degraded": degraded,
    }
