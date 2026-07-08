"""P1.4 — Deterministic assembly of day content package from P1.1–P1.3 artifacts."""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.day_model_v1_content_mapper import (
    DAY_MODEL_CONTENT_MAPPING_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_content_resolver import (
    DAY_MODEL_CONTENT_RESOLUTION_V1_CONTRACT,
)
from todayflow_backend.services.day_model_v1_interpreter import (
    DAY_MODEL_INTERPRETATION_V1_CONTRACT,
)

DAY_CONTENT_PACKAGE_V1_CONTRACT = "day_content_package_v1"

ENTRY_OUTPUT_FIELDS = ("key", "text_short", "text_medium", "tone", "version")

REQUIRED_PACKAGE_SLOTS = (
    "headline",
    "guidance",
    "risk_warning",
    "action_hint",
    "tempo_hint",
)

OPTIONAL_PACKAGE_SLOTS = ("reflection_hint",)

DAY_CONTENT_PACKAGE_V1_KEYS = frozenset(
    {
        "contract_version",
        "headline",
        "guidance",
        "risk_warning",
        "action_hint",
        "tempo_hint",
        "reflection_hint",
        "metadata",
        "degraded",
    }
)


class DayContentAssemblyError(ValueError):
    """Raised when assembly inputs are invalid or incomplete."""


def _require_artifact(
    payload: dict[str, Any],
    *,
    label: str,
    contract_version: str,
) -> None:
    if payload.get("contract_version") != contract_version:
        raise DayContentAssemblyError(
            f"{label}: expected contract_version={contract_version!r}, "
            f"got {payload.get('contract_version')!r}"
        )


def _project_entry(entry: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in ENTRY_OUTPUT_FIELDS if field not in entry]
    if missing:
        raise DayContentAssemblyError(f"content entry missing fields: {missing}")
    return {field: entry[field] for field in ENTRY_OUTPUT_FIELDS}


def _entries_for_slot(
    slot: str,
    mapping: dict[str, Any],
    resolution: dict[str, Any],
) -> list[dict[str, Any]]:
    keys: list[str] = list(mapping.get("required_slots", {}).get(slot, []))
    if slot in mapping.get("optional_slots", {}):
        keys.extend(mapping["optional_slots"][slot])

    if not keys:
        return []

    by_key = resolution.get("entries_by_key", {})
    entries: list[dict[str, Any]] = []
    for content_key in keys:
        entry = by_key.get(content_key)
        if entry is not None:
            entries.append(_project_entry(entry))
    return entries


def assemble_day_content_package_v1(
    interpretation: dict[str, Any],
    mapping: dict[str, Any],
    resolution: dict[str, Any],
) -> dict[str, Any]:
    """
    P1.4 — structured content package from interpretation, mapping, and resolved entries.

    Does not merge prose, modify entries, or call LLM/UI/API.
    """
    _require_artifact(
        interpretation,
        label="interpretation",
        contract_version=DAY_MODEL_INTERPRETATION_V1_CONTRACT,
    )
    _require_artifact(
        mapping,
        label="mapping",
        contract_version=DAY_MODEL_CONTENT_MAPPING_V1_CONTRACT,
    )
    _require_artifact(
        resolution,
        label="resolution",
        contract_version=DAY_MODEL_CONTENT_RESOLUTION_V1_CONTRACT,
    )

    missing_slots: list[str] = []
    slot_entries: dict[str, list[dict[str, Any]]] = {}

    for slot in REQUIRED_PACKAGE_SLOTS:
        entries = _entries_for_slot(slot, mapping, resolution)
        slot_entries[slot] = entries
        if not entries:
            missing_slots.append(slot)

    reflection_entries = _entries_for_slot("reflection_hint", mapping, resolution)
    reflection_hint = reflection_entries[0] if reflection_entries else None

    degraded = (
        bool(interpretation.get("degraded", False))
        or bool(mapping.get("degraded", False))
        or bool(resolution.get("degraded", False))
        or bool(missing_slots)
    )

    metadata = {
        "strategy": interpretation["strategy"],
        "opportunity_class": interpretation["opportunity_class"],
        "risk_class": interpretation["risk_class"],
        "tempo_instruction": interpretation["tempo_instruction"],
        "action_mode": interpretation["action_mode"],
        "reflection_mode": interpretation["reflection_mode"],
        "pressure_level": interpretation["pressure_level"],
        "confidence": interpretation["confidence"],
        "degraded": degraded,
        "content_keys": dict(mapping["content_keys"]),
        "missing_keys": list(resolution.get("missing_keys", mapping.get("missing_keys", []))),
        "missing_slots": missing_slots,
        "interpretation_degraded": bool(interpretation.get("degraded", False)),
        "mapping_degraded": bool(mapping.get("degraded", False)),
        "resolution_degraded": bool(resolution.get("degraded", False)),
    }

    headline_entries = slot_entries["headline"]
    if len(headline_entries) != 1:
        if "headline" not in missing_slots:
            missing_slots.append("headline")
        degraded = True
        metadata["degraded"] = True
        metadata["missing_slots"] = sorted(set(missing_slots))

    package: dict[str, Any] = {
        "contract_version": DAY_CONTENT_PACKAGE_V1_CONTRACT,
        "headline": headline_entries[0] if len(headline_entries) == 1 else None,
        "guidance": slot_entries["guidance"],
        "risk_warning": slot_entries["risk_warning"][0] if slot_entries["risk_warning"] else None,
        "action_hint": slot_entries["action_hint"][0] if slot_entries["action_hint"] else None,
        "tempo_hint": slot_entries["tempo_hint"][0] if slot_entries["tempo_hint"] else None,
        "reflection_hint": reflection_hint,
        "metadata": metadata,
        "degraded": degraded,
    }
    return package