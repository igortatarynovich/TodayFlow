"""Soft-heal for one-field gate misses — visible as healed:<rule>."""

from __future__ import annotations

from todayflow_backend.services.day_scenario_gate_maturity_c36 import (
    apply_soft_native_heals,
    apply_soft_scenario_heals,
    healed_failure_class,
    is_hard_native_validate_error,
    is_hard_scenario_validate_error,
)
from todayflow_backend.services.day_scenario_native_llm_c1 import (
    validate_native_scenario_llm_c1,
)
from todayflow_backend.services.day_scenario_v1 import (
    DAY_SCENARIO_V1_CONTRACT,
    DAY_SCENARIO_V1_VERSION,
    validate_day_scenario_v1,
)


def test_healed_failure_class_primary() -> None:
    assert healed_failure_class([]) is None
    assert (
        healed_failure_class(
            ["day_card_missing_conflict_link", "prop_color_without_origin_scene"]
        )
        == "healed:day_card_missing_conflict_link"
    )


def test_heal_day_card_and_number_conflict_link() -> None:
    payload = {
        "schema_version": "day_scenario_native_llm_c1",
        "conflict": {"title": "Спешка или пауза", "force_a": "", "force_b": ""},
        "scenes": [
            {
                "scene_id": "s1",
                "sphere": "work_decisions",
                "setup": "На работе письмо ждёт ответа.",
                "opportunity": "Ответить коротко.",
                "trap": "Отложить.",
                "chorus_refs": [],
            },
            {
                "scene_id": "s2",
                "sphere": "relationships",
                "setup": "Дома кто-то ждёт ясности.",
                "opportunity": "Сказать прямо.",
                "trap": "Молчать.",
                "chorus_refs": [],
            },
        ],
        "interpretive_chorus": {
            "day_card": {
                "named_factor": "Маг",
                "human_meaning": "Собрать волю в один жест",
                "archetype_role": "инициатор",
                "link_to_conflict": "",
            },
            "day_number": {
                "named_factor": "5",
                "human_meaning": "Перемена темпа",
                "archetype_role": "",
                "link_to_conflict": "",
            },
        },
    }
    healed, rules = apply_soft_native_heals(payload)
    assert "day_card_missing_conflict_link" in rules
    assert "day_number_missing_conflict_link" in rules
    assert healed["interpretive_chorus"]["day_card"]["link_to_conflict"] == "тон дня"
    assert healed["interpretive_chorus"]["day_number"]["link_to_conflict"] == "тон дня"
    assert not is_hard_native_validate_error("day_card_missing_conflict_link")
    errs = validate_native_scenario_llm_c1(healed)
    assert "day_card_missing_conflict_link" not in errs
    assert "day_number_missing_conflict_link" not in errs


def test_heal_scene_missing_conflict_link_sets_opaque_serves() -> None:
    payload = {
        "conflict": {"title": "Длинный конфликтный заголовок дня"},
        "scenes": [
            {
                "scene_id": "s1",
                "sphere": "work_decisions",
                "setup": "Совсем другой текст без якоря.",
                "opportunity": "x",
                "trap": "y",
                "chorus_refs": [],
                "serves_conflict": "",
            }
        ],
    }
    healed, rules = apply_soft_native_heals(payload)
    assert any(r.startswith("scene_missing_conflict_link:") for r in rules)
    assert healed["scenes"][0]["serves_conflict"] == "тон дня"


def test_heal_scenes_too_many_trims() -> None:
    scenes = [
        {"scene_id": f"s{i}", "sphere": "work_decisions", "setup": f"setup {i}"}
        for i in range(6)
    ]
    healed, rules = apply_soft_native_heals({"conflict": {}, "scenes": scenes})
    assert "scenes_too_many" in rules
    assert len(healed["scenes"]) == 4
    assert not is_hard_native_validate_error("scenes_too_many")
    assert is_hard_native_validate_error("scenes_too_few")


def test_heal_incomplete_forces_clears_pair() -> None:
    healed, rules = apply_soft_native_heals(
        {"conflict": {"title": "t", "force_a": "только A", "force_b": ""}, "scenes": []}
    )
    assert "conflict_forces_incomplete" in rules
    assert healed["conflict"]["force_a"] == ""
    assert healed["conflict"]["force_b"] == ""


def test_heal_opposing_forces_incomplete() -> None:
    scen = {
        "contract_version": DAY_SCENARIO_V1_CONTRACT,
        "version": DAY_SCENARIO_V1_VERSION,
        "conflict": {
            "short_name": "Живой конфликт",
            "driver_ids": ["d1"],
            "opposing_forces": {"a": "спешка", "b": ""},
        },
        "scenes": [],
        "props": {"status": "ok"},
        "foundation": {"ranked_drivers": [{"id": "d1", "fact_ru": "x"}]},
        "chorus": {},
    }
    healed, rules = apply_soft_scenario_heals(scen)
    assert "conflict_opposing_forces_incomplete" in rules
    assert healed["conflict"]["opposing_forces"] == {"a": "", "b": ""}
    assert not is_hard_scenario_validate_error("conflict_opposing_forces_incomplete")
    assert "conflict_opposing_forces_incomplete" not in validate_day_scenario_v1(healed)


def test_heal_drops_broken_props_not_whole_scenario() -> None:
    scen = {
        "contract_version": DAY_SCENARIO_V1_CONTRACT,
        "version": DAY_SCENARIO_V1_VERSION,
        "conflict": {
            "short_name": "Живой конфликт",
            "driver_ids": ["d1"],
            "opposing_forces": {"a": "", "b": ""},
        },
        "scenes": [
            {
                "scene_id": "scene.work",
                "sphere": "work_decisions",
                "serves_conflict": "тон дня",
                "setup": "s",
                "what_happens": "w",
                "recommended_action": "a",
            }
        ],
        "props": {
            "status": "ok",
            "color": {"name": "синий", "origin_scene_id": ""},
            "avoid_color": {"name": "красный", "origin_scene_id": "", "amplifies_trap": "t"},
            "goals": [{"text": "g", "origin_scene_id": ""}],
            "affirmations": [{"text": "a", "origin_scene_id": ""}],
            "humor": {"text": "h", "origin_scene_id": ""},
        },
        "foundation": {"ranked_drivers": [{"id": "d1", "fact_ru": "x"}]},
        "chorus": {},
    }
    healed, rules = apply_soft_scenario_heals(scen)
    assert "prop_color_without_origin_scene" in rules
    assert "prop_avoid_without_origin_scene" in rules
    assert "prop_goal_without_origin_scene" in rules
    assert "prop_affirmation_without_origin_scene" in rules
    assert "prop_humor_without_origin_scene" in rules
    props = healed["props"]
    assert "color" not in props
    assert "avoid_color" not in props
    assert props.get("goals") == []
    assert props.get("affirmations") == []
    assert "humor" not in props
    hard = [e for e in validate_day_scenario_v1(healed) if is_hard_scenario_validate_error(e)]
    assert hard == []


def test_seed_kill_and_structural_still_hard() -> None:
    assert is_hard_scenario_validate_error("conflict.short_name:invented_bank_binary")
    assert is_hard_scenario_validate_error("chorus:seed_paste_bridge")
    assert is_hard_scenario_validate_error("scene_serves_conflict_not_opaque:x")
    assert is_hard_native_validate_error("payload_not_dict")
    assert is_hard_native_validate_error("bad_schema_version")
    assert is_hard_native_validate_error("conflict_missing_title")
    assert is_hard_native_validate_error("scene_not_dict")
    assert is_hard_native_validate_error("scene_bad_sphere:xyz")
    assert is_hard_native_validate_error("scene_duplicate_id:s1")
    assert is_hard_native_validate_error("scene_missing_setup:s1")
    assert is_hard_native_validate_error("scenes_too_few")
