"""C3.3b — sphere selection + pairwise production eval."""

from __future__ import annotations

from copy import deepcopy

from todayflow_backend.services.day_scenario_native_llm_c1 import normalize_native_scenario_llm_c1
from todayflow_backend.services.day_scenario_pairwise_eval_c33b import (
    run_pairwise_eval_c33b,
    structural_diff_dimensions,
)
from todayflow_backend.services.day_scenario_personalization_c33 import (
    DEPTH_DEEP,
    DEPTH_GENERAL,
    build_personalization_evidence_pack_c33,
)
from todayflow_backend.services.day_scenario_sphere_selection_c33b import (
    DEFECT_SPHERE_OUTSIDE_PACK,
    attach_sphere_selection_to_pack,
    build_sphere_selection_c33b,
    run_sphere_selection_gate_c33b,
)
from tests.test_day_scenario_editorial_gate_c31 import _valid_native_good
from tests.test_day_scenario_personalization_c33a import (
    _interp_control,
    _interp_deep_a,
    _interp_deep_b,
)


SHARED_DAY = {
    "date": "2026-07-24",
    "location": "Moscow",
    "card": "Отшельник",
    "number": 7,
    "thesis_family": "communication",
    "day_domains": ["relationships"],
    "ritual_head_topic": "relationships",
}


def test_sphere_selection_differs_for_deep_profiles_same_day():
    pack_a = build_personalization_evidence_pack_c33(_interp_deep_a(), birth_time_present=True)
    pack_b = build_personalization_evidence_pack_c33(_interp_deep_b(), birth_time_present=True)
    pack_a = attach_sphere_selection_to_pack(
        pack_a,
        day_domains=SHARED_DAY["day_domains"],
        ritual_head_topic=SHARED_DAY["ritual_head_topic"],
        thesis_family=SHARED_DAY["thesis_family"],
    )
    pack_b = attach_sphere_selection_to_pack(
        pack_b,
        day_domains=SHARED_DAY["day_domains"],
        ritual_head_topic=SHARED_DAY["ritual_head_topic"],
        thesis_family=SHARED_DAY["thesis_family"],
    )
    sel_a = pack_a["sphere_selection"]
    sel_b = pack_b["sphere_selection"]
    assert sel_a["ranked_spheres"]
    assert sel_b["ranked_spheres"]
    # Same day keeps relationships available; personal weights reorder
    assert "relationships" in sel_a["allowed_spheres"] or "communication" in sel_a["allowed_spheres"]
    assert "work_decisions" in sel_b["allowed_spheres"]
    # Primary candidates should not be identical sets for A (smooth) vs B (control/work)
    assert set(sel_a["primary_candidates"]) != set(sel_b["primary_candidates"]) or (
        sel_a["ranked_spheres"][0]["sphere"] != sel_b["ranked_spheres"][0]["sphere"]
    )


def test_general_sphere_selection_is_day_only():
    pack = build_personalization_evidence_pack_c33(_interp_control())
    sel = build_sphere_selection_c33b(
        pack,
        day_domains=["relationships"],
        ritual_head_topic="relationships",
        thesis_family="communication",
    )
    assert sel["evidence_depth"] == DEPTH_GENERAL
    assert all(r["source"] in {"day", "family"} for r in sel["ranked_spheres"])
    assert sel["personal_sphere_count"] == 0


def test_sphere_outside_pack_without_justification_rejected():
    pack = build_personalization_evidence_pack_c33(_interp_deep_a(), birth_time_present=True)
    pack = attach_sphere_selection_to_pack(
        pack,
        day_domains=["relationships"],
        ritual_head_topic="relationships",
        thesis_family="communication",
    )
    # Force allowed list without money
    pack["sphere_selection"]["allowed_spheres"] = ["relationships", "communication"]
    pack["sphere_selection"]["primary_candidates"] = ["relationships", "communication"]

    native = _valid_native_good()
    native["personalization_depth"] = DEPTH_DEEP
    native["scenes"][0]["sphere"] = "money"
    native["scenes"][0]["scene_id"] = "scene.money"
    native["scenes"][0]["personalization"] = {
        "personalization_level": DEPTH_DEEP,
        "personalization_reason": "",
        "sphere_reason": "",
        "personalization_evidence_refs": [],
        "general_fallback_available": True,
    }
    defects = run_sphere_selection_gate_c33b(normalize_native_scenario_llm_c1(native), pack)
    assert any(d["code"] == DEFECT_SPHERE_OUTSIDE_PACK for d in defects)


def _deep_native_a() -> dict:
    native = _valid_native_good()
    native["personalization_depth"] = DEPTH_DEEP
    native["conflict"]["personalization"] = {
        "personalization_level": DEPTH_DEEP,
        "personalization_reason": "stop smoothing",
        "personalization_evidence_refs": ["claim.personal.moon7.smooth"],
        "habitual_force": "a",
        "required_movement": "b",
        "general_fallback_available": True,
    }
    native["scenes"][0]["personalization"] = {
        "personalization_level": DEPTH_DEEP,
        "personalization_reason": "relationships — rejection",
        "personalization_evidence_refs": ["claim.personal.venus.reject"],
        "sphere_reason": "sensitive relationships",
        "response_pattern": "smooth_conflict",
        "compensating_for": "smooth_conflict",
        "trap_pattern": "agree_for_silence",
        "general_fallback_available": True,
    }
    native["scenes"][0]["recommended_action"] = "Сказать одну конкретную фразу вместо молчания."
    return native


def _deep_native_b() -> dict:
    native = _valid_native_good()
    native["personalization_depth"] = DEPTH_DEEP
    native["scenes"][0]["sphere"] = "work_decisions"
    native["scenes"][0]["scene_id"] = "scene.work_decisions"
    native["conflict"]["force_a"] = "давить ясностью"
    native["conflict"]["force_b"] = "один вопрос до ответа"
    native["conflict"]["personalization"] = {
        "personalization_level": DEPTH_DEEP,
        "personalization_reason": "do not pressure",
        "personalization_evidence_refs": ["claim.personal.mars1.direct"],
        "habitual_force": "b",
        "required_movement": "a",
        "general_fallback_available": True,
    }
    native["scenes"][0]["trap"] = "Превратить ясность в давление."
    native["scenes"][0]["recommended_action"] = "Задать один вопрос до ответа; не решать за коллегу."
    native["scenes"][0]["personalization"] = {
        "personalization_level": DEPTH_DEEP,
        "personalization_reason": "work — over_control",
        "personalization_evidence_refs": ["claim.personal.sat.overload"],
        "sphere_reason": "responsibility overload at work",
        "response_pattern": "over_control",
        "compensating_for": "over_control",
        "trap_pattern": "pressure_clarity",
        "general_fallback_available": True,
    }
    # second scene also work/communication
    if len(native["scenes"]) > 1:
        native["scenes"][1]["sphere"] = "communication"
        native["scenes"][1]["scene_id"] = "scene.communication"
        native["scenes"][1]["personalization"] = {
            "personalization_level": DEPTH_DEEP,
            "personalization_reason": "communication support",
            "personalization_evidence_refs": ["claim.personal.mars1.direct"],
            "sphere_reason": "direct action in talk",
            "compensating_for": "direct_action",
            "general_fallback_available": True,
        }
    return native


def test_pairwise_production_eval_passes():
    pack_c = build_personalization_evidence_pack_c33(_interp_control())
    pack_a = build_personalization_evidence_pack_c33(_interp_deep_a(), birth_time_present=True)
    pack_b = build_personalization_evidence_pack_c33(_interp_deep_b(), birth_time_present=True)

    control = normalize_native_scenario_llm_c1(_valid_native_good())
    control["personalization_depth"] = DEPTH_GENERAL
    profile_a = normalize_native_scenario_llm_c1(_deep_native_a())
    profile_b = normalize_native_scenario_llm_c1(_deep_native_b())

    report = run_pairwise_eval_c33b(
        shared_day=SHARED_DAY,
        control=control,
        profile_a=profile_a,
        profile_b=profile_b,
        pack_control=pack_c,
        pack_a=pack_a,
        pack_b=pack_b,
    )
    assert report["diff_ab_dimensions"]
    assert len(report["diff_ab_dimensions"]) >= 2
    assert report["pairwise_checks"]["control_is_general"]
    assert report["pairwise_checks"]["a_and_b_differ_structurally"]
    assert report["pairwise_checks"]["no_cross_profile_evidence"]
    assert report["pass"] is True, report


def test_structural_diff_lists_expected_axes():
    a = normalize_native_scenario_llm_c1(_deep_native_a())
    b = normalize_native_scenario_llm_c1(_deep_native_b())
    dims = structural_diff_dimensions(a, b)
    assert "spheres" in dims or "actions" in dims
    assert "habitual_force" in dims
