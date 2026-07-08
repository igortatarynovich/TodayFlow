"""ILR-2 — Load Interpretation Rule registry from DATA/reference/interpretation/."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.interpretation_rule_registry_validator import (
    INTERPRETATION_RULE_REGISTRY_V1_CONTRACT,
    validate_interpretation_rule_registry_v1,
)
from todayflow_backend.data.reference_machine_loader import DATA_ROOT

INTERPRETATION_RULE_REGISTRY_PATH = (
    DATA_ROOT / "reference" / "interpretation" / "interpretation_rule_registry_v1.json"
)


class InterpretationRuleRegistryError(Exception):
    """Raised when interpretation rule registry is missing or invalid."""


def clear_interpretation_rule_registry_cache() -> None:
    load_interpretation_rule_registry_v1.cache_clear()
    load_interpretation_rules_v0.cache_clear()


@lru_cache(maxsize=1)
def load_interpretation_rule_registry_v1() -> dict[str, Any]:
    path = Path(os.getenv("TODAYFLOW_INTERPRETATION_RULE_REGISTRY_PATH", INTERPRETATION_RULE_REGISTRY_PATH))
    if not path.is_file():
        raise InterpretationRuleRegistryError(f"interpretation rule registry not found: {path}")
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    errors = validate_interpretation_rule_registry_v1(payload)
    if errors:
        raise InterpretationRuleRegistryError("; ".join(errors[:8]))
    return payload


def list_interpretation_rule_entries(
    registry: dict[str, Any] | None = None,
    *,
    allowed_statuses: frozenset[str] | None = None,
) -> list[dict[str, Any]]:
    payload = registry if registry is not None else load_interpretation_rule_registry_v1()
    statuses = allowed_statuses or frozenset({"active"})
    rules = payload.get("interpretation_rules") or {}
    out: list[dict[str, Any]] = []
    for ref_id in sorted(rules.keys()):
        rule = rules[ref_id]
        if not isinstance(rule, dict):
            continue
        if rule.get("status") not in statuses:
            continue
        out.append(dict(rule))
    return out


@lru_cache(maxsize=1)
def load_interpretation_rules_v0() -> tuple[dict[str, Any], ...]:
    """Return runtime rule dicts for interpretation engine (active rules only)."""
    return tuple(list_interpretation_rule_entries(allowed_statuses=frozenset({"active"})))


def get_interpretation_rule(ref_id: str, registry: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = registry if registry is not None else load_interpretation_rule_registry_v1()
    rules = payload.get("interpretation_rules") or {}
    rule = rules.get(ref_id)
    if not isinstance(rule, dict):
        raise InterpretationRuleRegistryError(f"interpretation rule not found: {ref_id!r}")
    return dict(rule)


def registry_contract_version(registry: dict[str, Any] | None = None) -> str:
    payload = registry if registry is not None else load_interpretation_rule_registry_v1()
    return str(payload.get("contract_version") or INTERPRETATION_RULE_REGISTRY_V1_CONTRACT)
