"""ILR-2 — Interpretation rule registry tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.interpretation_rule_registry_loader import (
    INTERPRETATION_RULE_REGISTRY_V1_CONTRACT,
    clear_interpretation_rule_registry_cache,
    get_interpretation_rule,
    list_interpretation_rule_entries,
    load_interpretation_rule_registry_v1,
)
from todayflow_backend.data.interpretation_rule_registry_validator import (
    validate_interpretation_rule_registry_v1,
)
from todayflow_backend.services.interpretation_reference_v0 import (
    clear_interpretation_rule_registry_cache as clear_service_cache,
    get_interpretation_rules_v0,
)


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    clear_interpretation_rule_registry_cache()
    clear_service_cache()
    yield
    clear_interpretation_rule_registry_cache()
    clear_service_cache()


@pytest.fixture
def registry() -> dict:
    return load_interpretation_rule_registry_v1()


def test_registry_contract_and_rules(registry: dict) -> None:
    assert registry["contract_version"] == INTERPRETATION_RULE_REGISTRY_V1_CONTRACT
    assert registry["domain"] == "interpretation"
    rules = list_interpretation_rule_entries(registry)
    assert len(rules) >= 14
    assert get_interpretation_rule("beh.compat_echo_communication_yes.v1", registry)["spawn_hypothesis_ids"] == [
        "attachment_lens:v0"
    ]


def test_runtime_rules_load_from_registry() -> None:
    runtime = get_interpretation_rules_v0()
    assert len(runtime) >= 14
    ref_ids = {r["interpretation_ref_id"] for r in runtime}
    assert "beh.focus_started.v1" in ref_ids
    assert "beh.compat_deep_open.v1" in ref_ids
    for rule in runtime:
        meanings = rule["candidate_meanings"]
        assert len(meanings) >= 2
        assert rule.get("trigger_payload_values") is None or isinstance(rule["trigger_payload_values"], frozenset)


def test_validator_rejects_bad_weight_sum(registry: dict) -> None:
    bad = copy.deepcopy(registry)
    rule = bad["interpretation_rules"]["beh.focus_started.v1"]
    rule["candidate_meanings"][0]["prior_weight"] = 0.99
    errors = validate_interpretation_rule_registry_v1(bad)
    assert any("prior_weight sum" in e for e in errors)
