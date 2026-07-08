"""B1.5 — Evolution Product Effects Registry tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1
from todayflow_backend.data.evolution_product_effects_loader import (
    COMMERCE_EFFECTS_V1_KEYS,
    ENGINE_EFFECTS_V1_KEYS,
    EVOLUTION_PRODUCT_EFFECTS_REGISTRY_V1,
    INTELLIGENCE_EFFECTS_V1_KEYS,
    STAGE_PRODUCT_EFFECTS_V1_KEYS,
    UNLOCK_EFFECTS_V1_KEYS,
    clear_evolution_product_effects_cache,
    diff_stage_product_effects_v1,
    get_stage_product_effects,
    list_stage_product_effects_ordered,
    load_evolution_product_effects_registry_v1,
    validate_evolution_product_effects_registry_v1,
)
from todayflow_backend.data.evolution_cd_validator import CANONICAL_STAGE_ORDER


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    clear_evolution_cd_cache()
    clear_evolution_product_effects_cache()
    yield
    clear_evolution_cd_cache()
    clear_evolution_product_effects_cache()


@pytest.fixture
def registry() -> dict:
    return load_evolution_product_effects_registry_v1()


@pytest.fixture
def cd() -> dict:
    return load_evolution_cd_v1()


def test_all_seven_stages_present(registry: dict) -> None:
    effects = list_stage_product_effects_ordered(registry)
    assert len(effects) == 7
    assert [e["stage_code"] for e in effects] == list(CANONICAL_STAGE_ORDER)


def test_valid_registry_passes(registry: dict, cd: dict) -> None:
    assert validate_evolution_product_effects_registry_v1(registry, evolution_cd=cd) == []


def test_unknown_stage_invalid(registry: dict, cd: dict) -> None:
    broken = copy.deepcopy(registry)
    broken["stage_product_effects"]["novice"] = broken["stage_product_effects"]["seeker"]
    del broken["stage_product_effects"]["master"]
    errors = validate_evolution_product_effects_registry_v1(broken, evolution_cd=cd)
    assert any("canonical stage set" in e or "expected 7" in e for e in errors)


def test_b1_1_alignment(registry: dict, cd: dict) -> None:
    for stage_code in CANONICAL_STAGE_ORDER:
        effects = get_stage_product_effects(stage_code, registry)
        cd_stage = cd["evolution_stages"][stage_code]
        assert effects["engine_effects"]["llm_budget_tier"] == cd_stage["llm_budget_tier"]
        assert effects["engine_effects"]["max_context_lines"] == cd_stage["max_context_lines"]
        assert effects["commerce_effects"]["commerce_visibility"] == cd_stage["commerce_visibility"]
        assert effects["intelligence_effects"]["context_slice_depth"] == cd_stage["allowed_depth"]


def test_architect_exceeds_practitioner_on_product_value(registry: dict) -> None:
    diff = diff_stage_product_effects_v1("practitioner", "architect", registry)
    unlock = diff["changed_effects"].get("unlock_effects", {})
    intel = diff["changed_effects"].get("intelligence_effects", {})

    assert unlock["path_themes_max_active"]["to"] > unlock["path_themes_max_active"]["from"]
    assert unlock["calendar_insight_tier"]["to"] == "full"
    assert unlock["goal_system_tier"]["to"] == "advanced"
    assert intel["memory_window_days"]["to"] > intel["memory_window_days"]["from"]
    assert intel["answer_length"]["to"] == "deep"


def test_cycle_lengths_valid(registry: dict, cd: dict) -> None:
    allowed = {7, 21, 30, 90}
    for effects in list_stage_product_effects_ordered(registry):
        for length in effects["unlock_effects"]["cycle_lengths_available"]:
            assert length in allowed
    assert validate_evolution_product_effects_registry_v1(registry, evolution_cd=cd) == []


def test_no_runtime_api_fields(registry: dict, cd: dict) -> None:
    broken = copy.deepcopy(registry)
    broken["openapi_field"] = "evolution_stage"
    errors = validate_evolution_product_effects_registry_v1(broken, evolution_cd=cd)
    assert any("forbidden field" in e for e in errors)


def test_output_shape_stable(registry: dict) -> None:
    assert registry["contract_version"] == EVOLUTION_PRODUCT_EFFECTS_REGISTRY_V1
    for effects in list_stage_product_effects_ordered(registry):
        assert set(effects.keys()) == set(STAGE_PRODUCT_EFFECTS_V1_KEYS)
        assert set(effects["intelligence_effects"].keys()) == INTELLIGENCE_EFFECTS_V1_KEYS
        assert set(effects["engine_effects"].keys()) == ENGINE_EFFECTS_V1_KEYS
        assert set(effects["unlock_effects"].keys()) == UNLOCK_EFFECTS_V1_KEYS
        assert set(effects["commerce_effects"].keys()) == COMMERCE_EFFECTS_V1_KEYS


def test_monotonic_progression(registry: dict, cd: dict) -> None:
    assert validate_evolution_product_effects_registry_v1(registry, evolution_cd=cd) == []


def test_practitioner_vs_architect_user_facing_summary_differs(registry: dict) -> None:
    practitioner = get_stage_product_effects("practitioner", registry)
    architect = get_stage_product_effects("architect", registry)
    assert practitioner["user_facing_summary"] != architect["user_facing_summary"]
    assert "System mode" in architect["user_facing_summary"]
