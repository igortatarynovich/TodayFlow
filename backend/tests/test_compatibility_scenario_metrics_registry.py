"""Compat-ref-1 — Compatibility scenario metrics registry tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.compatibility_scenario_metrics_registry_loader import (
    COMPATIBILITY_SCENARIO_METRICS_REGISTRY_V1_CONTRACT,
    clear_compatibility_scenario_metrics_registry_cache,
    get_default_scenario_id,
    get_scenario_blends,
    get_scenario_funnel_domains,
    get_scenario_hero_weights,
    load_compatibility_scenario_metrics_registry_v1,
)
from todayflow_backend.data.compatibility_scenario_metrics_registry_validator import (
    validate_compatibility_scenario_metrics_registry_v1,
)


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    clear_compatibility_scenario_metrics_registry_cache()
    yield
    clear_compatibility_scenario_metrics_registry_cache()


@pytest.fixture
def registry() -> dict:
    return load_compatibility_scenario_metrics_registry_v1()


def test_registry_contract(registry: dict) -> None:
    assert registry["contract_version"] == COMPATIBILITY_SCENARIO_METRICS_REGISTRY_V1_CONTRACT
    assert registry["domain"] == "compatibility"
    assert get_default_scenario_id() == "love"
    assert "love" in get_scenario_blends()
    assert "office" in get_scenario_funnel_domains()


def test_hero_weights_sum_to_one(registry: dict) -> None:
    for scenario_id, weights in get_scenario_hero_weights().items():
        total = sum(weights.values())
        assert abs(total - 1.0) < 0.06, scenario_id


def test_validator_rejects_missing_default(registry: dict) -> None:
    bad = copy.deepcopy(registry)
    bad["default_scenario_id"] = "missing_scenario"
    errors = validate_compatibility_scenario_metrics_registry_v1(bad)
    assert any("default_scenario_id" in e for e in errors)
