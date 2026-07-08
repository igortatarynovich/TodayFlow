"""Compat-ref-1 — Load compatibility scenario metrics from DATA/reference/compatibility/."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.compatibility_scenario_metrics_registry_validator import (
    COMPATIBILITY_SCENARIO_METRICS_REGISTRY_V1_CONTRACT,
    validate_compatibility_scenario_metrics_registry_v1,
)
from todayflow_backend.data.reference_machine_loader import DATA_ROOT

COMPATIBILITY_SCENARIO_METRICS_REGISTRY_PATH = (
    DATA_ROOT
    / "reference"
    / "compatibility"
    / "compatibility_scenario_metrics_registry_v1.json"
)

Blend = dict[str, float]


class CompatibilityScenarioMetricsRegistryError(Exception):
    """Raised when compatibility scenario metrics registry is missing or invalid."""


def clear_compatibility_scenario_metrics_registry_cache() -> None:
    load_compatibility_scenario_metrics_registry_v1.cache_clear()
    get_scenario_blends.cache_clear()
    get_scenario_hero_weights.cache_clear()
    get_scenario_funnel_domains.cache_clear()


@lru_cache(maxsize=1)
def load_compatibility_scenario_metrics_registry_v1() -> dict[str, Any]:
    path = Path(
        os.getenv(
            "TODAYFLOW_COMPATIBILITY_SCENARIO_METRICS_REGISTRY_PATH",
            COMPATIBILITY_SCENARIO_METRICS_REGISTRY_PATH,
        )
    )
    if not path.is_file():
        raise CompatibilityScenarioMetricsRegistryError(
            f"compatibility scenario metrics registry not found: {path}"
        )
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    errors = validate_compatibility_scenario_metrics_registry_v1(payload)
    if errors:
        raise CompatibilityScenarioMetricsRegistryError("; ".join(errors[:8]))
    return payload


def _to_blend(raw: dict[str, Any]) -> Blend:
    return {str(k): float(v) for k, v in raw.items()}


@lru_cache(maxsize=1)
def get_scenario_blends() -> dict[str, dict[str, Blend]]:
    payload = load_compatibility_scenario_metrics_registry_v1()
    raw = payload.get("scenario_blends") or {}
    return {
        scenario_id: {slot: _to_blend(weights) for slot, weights in slots.items()}
        for scenario_id, slots in raw.items()
        if isinstance(slots, dict)
    }


@lru_cache(maxsize=1)
def get_scenario_hero_weights() -> dict[str, Blend]:
    payload = load_compatibility_scenario_metrics_registry_v1()
    raw = payload.get("scenario_hero_weights") or {}
    return {scenario_id: _to_blend(weights) for scenario_id, weights in raw.items() if isinstance(weights, dict)}


@lru_cache(maxsize=1)
def get_scenario_funnel_domains() -> dict[str, list[str]]:
    payload = load_compatibility_scenario_metrics_registry_v1()
    raw = payload.get("scenario_funnel_domains") or {}
    return {
        scenario_id: list(domains)
        for scenario_id, domains in raw.items()
        if isinstance(domains, list)
    }


def get_default_scenario_id() -> str:
    payload = load_compatibility_scenario_metrics_registry_v1()
    return str(payload.get("default_scenario_id") or "love")
