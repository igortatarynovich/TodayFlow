"""B1.1 — Evolution CD reference tables (stages, path themes, stage gates)."""

from __future__ import annotations

import copy

import pytest

from todayflow_backend.data.evolution_cd_loader import (
    EVOLUTION_CD_V1_CONTRACT,
    EVOLUTION_PATH_THEME_V1_KEYS,
    EVOLUTION_STAGE_V1_KEYS,
    STAGE_GATE_V1_KEYS,
    clear_evolution_cd_cache,
    get_evolution_path_theme,
    get_evolution_stage,
    get_stage_gate,
    list_evolution_path_themes,
    list_evolution_stages_ordered,
    list_stage_gates_ordered,
    load_evolution_cd_v1,
)
from todayflow_backend.data.evolution_cd_validator import (
    ALLOWED_CYCLE_LENGTHS,
    ALLOWED_PROGRESSION_SIGNAL_TYPES,
    CANONICAL_STAGE_ORDER,
    FORBIDDEN_GATE_SIGNAL_PATTERN,
    validate_evolution_cd_v1,
)


@pytest.fixture(autouse=True)
def _clear_cd_cache() -> None:
    clear_evolution_cd_cache()
    yield
    clear_evolution_cd_cache()


@pytest.fixture
def cd() -> dict:
    return load_evolution_cd_v1()


def test_all_seven_stages_present_and_ordered(cd: dict) -> None:
    stages = list_evolution_stages_ordered(cd)
    assert len(stages) == 7
    assert [s["code"] for s in stages] == list(CANONICAL_STAGE_ORDER)
    assert [s["order"] for s in stages] == list(range(1, 8))


def test_stage_codes_unique(cd: dict) -> None:
    codes = [s["code"] for s in list_evolution_stages_ordered(cd)]
    assert len(codes) == len(set(codes))


def test_path_theme_codes_unique(cd: dict) -> None:
    themes = list_evolution_path_themes(cd)
    codes = [t["code"] for t in themes]
    assert len(codes) == len(set(codes))
    assert len(codes) == 10


def test_stage_gates_sequential_only(cd: dict) -> None:
    gates = list_stage_gates_ordered(cd)
    transitions = [(g["from_stage"], g["to_stage"]) for g in gates]
    expected = list(zip(CANONICAL_STAGE_ORDER[:-1], CANONICAL_STAGE_ORDER[1:]))
    assert transitions == expected


def test_stage_gates_no_achievement_signals(cd: dict) -> None:
    for gate in list_stage_gates_ordered(cd):
        for sig in gate["required_signal_types"]:
            assert "achievement" not in sig.lower()
            assert not FORBIDDEN_GATE_SIGNAL_PATTERN.search(sig)


def test_stage_gates_no_commerce_signals(cd: dict) -> None:
    forbidden = ("commerce", "purchase", "payment", "subscription")
    for gate in list_stage_gates_ordered(cd):
        for sig in gate["required_signal_types"]:
            lowered = sig.lower()
            assert not any(token in lowered for token in forbidden)


def test_stage_gate_required_signals_valid(cd: dict) -> None:
    for gate in list_stage_gates_ordered(cd):
        for sig in gate["required_signal_types"]:
            assert sig in ALLOWED_PROGRESSION_SIGNAL_TYPES


def test_path_theme_compatible_stages_valid(cd: dict) -> None:
    stage_codes = {s["code"] for s in list_evolution_stages_ordered(cd)}
    for theme in list_evolution_path_themes(cd):
        for stage in theme["compatible_stages"]:
            assert stage in stage_codes


def test_path_theme_suggested_cycle_lengths_valid(cd: dict) -> None:
    for theme in list_evolution_path_themes(cd):
        for length in theme["suggested_cycle_lengths"]:
            assert length in ALLOWED_CYCLE_LENGTHS


def test_output_shape_stable(cd: dict) -> None:
    assert cd["contract_version"] == EVOLUTION_CD_V1_CONTRACT
    assert cd["domain"] == "evolution"

    for stage in list_evolution_stages_ordered(cd):
        assert set(stage.keys()) == set(EVOLUTION_STAGE_V1_KEYS)

    for theme in list_evolution_path_themes(cd):
        assert set(theme.keys()) == set(EVOLUTION_PATH_THEME_V1_KEYS)

    for gate in list_stage_gates_ordered(cd):
        assert set(gate.keys()) == set(STAGE_GATE_V1_KEYS)


def test_loader_validates_on_load() -> None:
    assert validate_evolution_cd_v1(load_evolution_cd_v1()) == []


def test_get_helpers_resolve_entries(cd: dict) -> None:
    seeker = get_evolution_stage("seeker", cd)
    assert seeker["order"] == 1

    discipline = get_evolution_path_theme("discipline", cd)
    assert discipline["domain"] == "behavior"

    gate = get_stage_gate("gate-seeker-observer-v1", cd)
    assert gate["from_stage"] == "seeker"
    assert gate["to_stage"] == "observer"


def test_validator_rejects_achievement_gate_signal(cd: dict) -> None:
    broken = copy.deepcopy(cd)
    broken["stage_gates"][0]["required_signal_types"] = ["achievement_unlocked"]
    errors = validate_evolution_cd_v1(broken)
    assert any("forbidden" in e or "invalid signal" in e for e in errors)


def test_validator_rejects_non_sequential_gate(cd: dict) -> None:
    broken = copy.deepcopy(cd)
    broken["stage_gates"][0]["to_stage"] = "practitioner"
    errors = validate_evolution_cd_v1(broken)
    assert any("sequential" in e for e in errors)
