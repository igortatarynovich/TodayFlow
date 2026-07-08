"""C1.5 — Ritual Definition registry tests."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.ascetic_definition_registry_loader import clear_ascetic_definition_registry_cache
from todayflow_backend.data.evolution_cd_loader import clear_evolution_cd_cache, load_evolution_cd_v1
from todayflow_backend.data.habit_definition_registry_loader import clear_habit_definition_registry_cache
from todayflow_backend.data.practice_definition_registry_loader import clear_practice_definition_registry_cache
from todayflow_backend.data.ritual_definition_registry_loader import (
    RITUAL_DEFINITION_REGISTRY_V1_CONTRACT,
    clear_ritual_definition_registry_cache,
    get_ritual_definition,
    list_ritual_definitions_ordered,
    list_rituals_by_category,
    list_rituals_for_path,
    load_ritual_definition_registry_v1,
)
from todayflow_backend.data.ritual_definition_registry_validator import (
    CANONICAL_RITUAL_DEFINITION_CODES,
    RITUAL_DEFINITION_ALLOWED_SIGNALS,
    RITUAL_DEFINITION_V1_KEYS,
    validate_ritual_definition_registry_v1,
)
from todayflow_backend.data.ascetic_definition_registry_loader import load_ascetic_definition_registry_v1
from todayflow_backend.data.habit_definition_registry_loader import load_habit_definition_registry_v1
from todayflow_backend.data.practice_definition_registry_loader import load_practice_definition_registry_v1


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    clear_evolution_cd_cache()
    clear_practice_definition_registry_cache()
    clear_habit_definition_registry_cache()
    clear_ascetic_definition_registry_cache()
    clear_ritual_definition_registry_cache()
    yield
    clear_evolution_cd_cache()
    clear_practice_definition_registry_cache()
    clear_habit_definition_registry_cache()
    clear_ascetic_definition_registry_cache()
    clear_ritual_definition_registry_cache()


@pytest.fixture
def registry() -> dict:
    return load_ritual_definition_registry_v1()


def test_contract_and_eight_rituals(registry: dict) -> None:
    assert registry["contract_version"] == RITUAL_DEFINITION_REGISTRY_V1_CONTRACT
    rituals = list_ritual_definitions_ordered(registry)
    assert len(rituals) == 8
    assert [r["code"] for r in rituals] == list(CANONICAL_RITUAL_DEFINITION_CODES)


def test_ritual_schema_keys(registry: dict) -> None:
    for ritual in list_ritual_definitions_ordered(registry):
        assert set(ritual.keys()) == RITUAL_DEFINITION_V1_KEYS


def test_component_count_matches_components(registry: dict) -> None:
    for ritual in list_ritual_definitions_ordered(registry):
        assert ritual["component_count"] == len(ritual["components"])


def test_all_rituals_produce_streak_signal(registry: dict) -> None:
    for ritual in list_ritual_definitions_ordered(registry):
        assert "ritual_streak_confirmed" in ritual["produces_signals"]
        assert ritual["produces_signals"] == ["practice_completed", "ritual_streak_confirmed"]


def test_evening_reflection_ritual_components(registry: dict) -> None:
    ritual = get_ritual_definition("evening_reflection_ritual", registry)
    codes = [(c["component_type"], c["component_code"]) for c in ritual["components"]]
    assert ("practice", "reflection") in codes
    assert ("habit", "evening_reflection") in codes


def test_no_phone_evening_uses_ascetics(registry: dict) -> None:
    ritual = get_ritual_definition("no_phone_evening_ritual", registry)
    ascetic_codes = [
        c["component_code"] for c in ritual["components"] if c["component_type"] == "ascetic"
    ]
    assert "no_social_media_evening" in ascetic_codes
    assert "no_late_night_scrolling" in ascetic_codes


def test_compatible_paths_reference_b1_1(registry: dict) -> None:
    cd = load_evolution_cd_v1()
    path_codes = set((cd.get("evolution_path_themes") or {}).keys())
    for ritual in list_ritual_definitions_ordered(registry):
        assert set(ritual["compatible_paths"]).issubset(path_codes)


def test_list_rituals_by_category_evening(registry: dict) -> None:
    evening = list_rituals_by_category("evening", registry)
    codes = {r["code"] for r in evening}
    assert "evening_reflection_ritual" in codes
    assert "no_phone_evening_ritual" in codes


def test_list_rituals_for_path_discipline(registry: dict) -> None:
    rituals = list_rituals_for_path("discipline", registry)
    assert any(r["code"] == "morning_grounding_ritual" for r in rituals)


def test_validator_rejects_unknown_practice_component(registry: dict) -> None:
    refs = _registry_refs()
    bad = copy.deepcopy(registry)
    bad["ritual_definitions"]["morning_grounding_ritual"]["components"][0]["component_code"] = "missing"
    errors = validate_ritual_definition_registry_v1(bad, **refs)
    assert any("missing" in e for e in errors)


def test_validator_rejects_component_count_mismatch(registry: dict) -> None:
    refs = _registry_refs()
    bad = copy.deepcopy(registry)
    bad["ritual_definitions"]["morning_grounding_ritual"]["component_count"] = 99
    errors = validate_ritual_definition_registry_v1(bad, **refs)
    assert any("component_count must match" in e for e in errors)


def test_validator_rejects_habit_streak_signal(registry: dict) -> None:
    refs = _registry_refs()
    bad = copy.deepcopy(registry)
    bad["ritual_definitions"]["morning_grounding_ritual"]["produces_signals"] = [
        "practice_completed",
        "habit_streak_confirmed",
    ]
    errors = validate_ritual_definition_registry_v1(bad, **refs)
    assert any("habit_streak_confirmed" in e for e in errors)


def test_validator_rejects_ordered_without_order(registry: dict) -> None:
    refs = _registry_refs()
    bad = copy.deepcopy(registry)
    bad["ritual_definitions"]["morning_grounding_ritual"]["components"][0]["order"] = None
    errors = validate_ritual_definition_registry_v1(bad, **refs)
    assert any("must have positive order" in e for e in errors)


def test_allowed_signals_subset(registry: dict) -> None:
    for ritual in list_ritual_definitions_ordered(registry):
        for sig in ritual["produces_signals"]:
            assert sig in RITUAL_DEFINITION_ALLOWED_SIGNALS


def _registry_refs() -> dict:
    cd = load_evolution_cd_v1()
    return {
        "path_theme_codes": frozenset((cd.get("evolution_path_themes") or {}).keys()),
        "practice_codes": frozenset(
            (load_practice_definition_registry_v1().get("practice_definitions") or {}).keys()
        ),
        "habit_codes": frozenset(
            (load_habit_definition_registry_v1().get("habit_definitions") or {}).keys()
        ),
        "ascetic_codes": frozenset(
            (load_ascetic_definition_registry_v1().get("ascetic_definitions") or {}).keys()
        ),
    }
