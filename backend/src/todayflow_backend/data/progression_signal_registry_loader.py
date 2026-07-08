"""B1.3 — Load and validate progression signal registry."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.evolution_cd_validator import ALLOWED_PROGRESSION_SIGNAL_TYPES
from todayflow_backend.data.reference_machine_loader import DATA_ROOT

PROGRESSION_SIGNAL_REGISTRY_PATH = (
    DATA_ROOT / "reference" / "evolution" / "progression_signal_registry_v1.json"
)


class ProgressionSignalRegistryError(Exception):
    """Raised when progression signal registry is missing or invalid."""


def clear_progression_signal_registry_cache() -> None:
    load_progression_signal_registry_v1.cache_clear()


@lru_cache(maxsize=1)
def load_progression_signal_registry_v1() -> dict[str, Any]:
    path = Path(
        os.getenv("TODAYFLOW_PROGRESSION_SIGNAL_REGISTRY_PATH", PROGRESSION_SIGNAL_REGISTRY_PATH)
    )
    if not path.is_file():
        raise ProgressionSignalRegistryError(f"progression signal registry not found: {path}")
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    errors = validate_progression_signal_registry_v1(payload)
    if errors:
        raise ProgressionSignalRegistryError("; ".join(errors[:8]))
    return payload


def get_signal_type_definition(
    code: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = registry if registry is not None else load_progression_signal_registry_v1()
    types = payload.get("signal_types") or {}
    entry = types.get(code)
    if not isinstance(entry, dict):
        raise ProgressionSignalRegistryError(f"signal type not found: {code!r}")
    return dict(entry)



PROGRESSION_SIGNAL_REGISTRY_V1_CONTRACT = "progression_signal_registry_v1"

ALLOWED_SOURCE_ENGINES = frozenset({"practice", "goal", "ritual", "calendar", "pattern"})

ALLOWED_REGISTRY_STATUSES = frozenset({"draft", "active"})

SIGNAL_TYPE_V1_KEYS = frozenset(
    {
        "code",
        "title",
        "source_engine",
        "description",
        "feeds_gate_eligibility",
        "feeds_stage_directly",
        "min_confidence_for_gate",
        "status",
        "version",
    }
)

PROGRESSION_SIGNAL_REGISTRY_V1_TOP_KEYS = frozenset(
    {
        "contract_version",
        "domain",
        "version",
        "status",
        "description",
        "signal_types",
    }
)


def validate_progression_signal_registry_v1(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if payload.get("contract_version") != PROGRESSION_SIGNAL_REGISTRY_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in PROGRESSION_SIGNAL_REGISTRY_V1_TOP_KEYS:
        if key not in payload:
            errors.append(f"missing top-level field: {key}")

    if payload.get("domain") != "evolution":
        errors.append("domain must be evolution")

    signal_types = payload.get("signal_types")
    if not isinstance(signal_types, dict):
        errors.append("signal_types must be object")
        return errors

    if set(signal_types.keys()) != set(ALLOWED_PROGRESSION_SIGNAL_TYPES):
        errors.append("signal_types must match B1.1 progression signal types exactly")

    for code, entry in signal_types.items():
        prefix = f"signal_type[{code}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: must be object")
            continue

        for field in SIGNAL_TYPE_V1_KEYS:
            if field not in entry:
                errors.append(f"{prefix}: missing field {field!r}")

        if entry.get("code") != code:
            errors.append(f"{prefix}: code mismatch")

        if code not in ALLOWED_PROGRESSION_SIGNAL_TYPES:
            errors.append(f"{prefix}: not in B1.1 allowed types")

        if entry.get("source_engine") not in ALLOWED_SOURCE_ENGINES:
            errors.append(f"{prefix}: invalid source_engine")

        if entry.get("status") not in ALLOWED_REGISTRY_STATUSES:
            errors.append(f"{prefix}: invalid status")

        if entry.get("feeds_stage_directly") is not False:
            errors.append(f"{prefix}: feeds_stage_directly must be false")

        if entry.get("feeds_gate_eligibility") is not True:
            errors.append(f"{prefix}: feeds_gate_eligibility must be true")

        min_conf = entry.get("min_confidence_for_gate")
        if not isinstance(min_conf, (int, float)) or min_conf < 0 or min_conf > 1:
            errors.append(f"{prefix}: min_confidence_for_gate must be 0..1")

    return errors
