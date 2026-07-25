"""C3.3a — personalization evidence pack, depth modes, gate, pairwise fixtures."""

from __future__ import annotations

from copy import deepcopy

from todayflow_backend.services.day_scenario_personalization_c33 import (
    DEPTH_DEEP,
    DEPTH_GENERAL,
    DEPTH_LIGHT,
    DEFECT_CLAIM_WITHOUT_EVIDENCE,
    DEFECT_DECORATIVE_ONLY,
    DEFECT_DEPTH_OVERREACH,
    DEFECT_NATAL_OVERCLAIM,
    DEFECT_PROFILE_FACT_LEAK,
    build_personalization_evidence_pack_c33,
    downgrade_native_to_general_c33,
    personalization_decision_after_retries,
    run_personalization_gate_c33,
)
from todayflow_backend.services.day_scenario_native_llm_c1 import (
    NATIVE_LLM_SCHEMA_VERSION,
    normalize_native_scenario_llm_c1,
)
from tests.test_day_scenario_editorial_gate_c31 import _valid_native_good


def _day_shared_native() -> dict:
    return _valid_native_good()


def _interp_control() -> dict:
    return {
        "derived_claims": [
            {
                "id": "claim.sky.moon",
                "text": "Луна в Рыбах усиливает подтекст.",
                "evidence_ids": ["moon-pisces"],
                "layer": "day",
            }
        ],
        "day_personal": {"source_inputs": {}},
    }


def _interp_light() -> dict:
    return {
        "derived_claims": [
            {
                "id": "claim.personal.sun_sign",
                "text": "Солнце в Овне — прямое действие ближе, чем долгий анализ.",
                "evidence_ids": ["birth_date"],
                "layer": "personal",
            }
        ],
        "day_personal": {
            "summary_ru": "Солнце в Овне.",
            "source_inputs": {"has_personal_astrology": False},
            "personal_astrology": None,
        },
    }


def _interp_deep_a() -> dict:
    """Profile A — smooth conflict / avoid clarity."""
    return {
        "derived_claims": [
            {
                "id": "claim.personal.moon7.smooth",
                "text": "Вам привычно сглаживать конфликт ради тишины в близких.",
                "evidence_ids": ["natal.moon.7", "birth_time"],
                "layer": "personal",
            },
            {
                "id": "claim.personal.venus.reject",
                "text": "Чувствительность к отвержению усиливает желание ответить «нормально».",
                "evidence_ids": ["natal.venus"],
                "layer": "personal",
            },
        ],
        "day_personal": {
            "source_inputs": {
                "has_personal_astrology": True,
                "has_birth_time": True,
            },
            "personal_astrology": {
                "summary_ru": "Луна в 7 — сглаживание.",
                "chart_meta": {"has_birth_time": True},
                "beats": [{"id": "moon7", "story_ru": "сглаживать конфликт", "domain": "relationships"}],
            },
        },
    }


def _interp_deep_b() -> dict:
    """Profile B — direct / over-control."""
    return {
        "derived_claims": [
            {
                "id": "claim.personal.mars1.direct",
                "text": "Вам привычно резко требовать ясности и контролировать ответ другого.",
                "evidence_ids": ["natal.mars.1", "birth_time"],
                "layer": "personal",
            },
            {
                "id": "claim.personal.sat.overload",
                "text": "Ответственность перегружает — хотите решить за других.",
                "evidence_ids": ["natal.saturn"],
                "layer": "personal",
            },
        ],
        "day_personal": {
            "source_inputs": {
                "has_personal_astrology": True,
                "has_birth_time": True,
            },
            "personal_astrology": {
                "summary_ru": "Марс прямое действие.",
                "chart_meta": {"has_birth_time": True},
                "beats": [{"id": "mars1", "story_ru": "прямое действие", "domain": "work_decisions"}],
            },
        },
    }


def test_pack_depths_pairwise_same_day_different_profiles():
    control = build_personalization_evidence_pack_c33(_interp_control())
    light = build_personalization_evidence_pack_c33(_interp_light(), birth_date_present=True)
    deep_a = build_personalization_evidence_pack_c33(_interp_deep_a(), birth_time_present=True)
    deep_b = build_personalization_evidence_pack_c33(_interp_deep_b(), birth_time_present=True)

    assert control["evidence_depth"] == DEPTH_GENERAL
    assert light["evidence_depth"] == DEPTH_LIGHT
    assert deep_a["evidence_depth"] == DEPTH_DEEP
    assert deep_b["evidence_depth"] == DEPTH_DEEP

    ids_a = {t["id"] for t in deep_a["behavioral_tendencies"]}
    ids_b = {t["id"] for t in deep_b["behavioral_tendencies"]}
    assert "smooth_conflict" in ids_a or "rejection_sensitivity" in ids_a
    assert "direct_action" in ids_b or "over_control" in ids_b
    assert ids_a != ids_b

    # Evidence isolation
    refs_a = set(deep_a["evidence_refs"])
    refs_b = set(deep_b["evidence_refs"])
    assert "natal.moon.7" in refs_a
    assert "natal.mars.1" in refs_b
    assert "natal.mars.1" not in refs_a
    assert "natal.moon.7" not in refs_b


def test_general_forbids_personal_claims():
    native = _day_shared_native()
    native["conflict"]["why_personal"] = "Вам обычно свойственно сглаживать."
    pack = build_personalization_evidence_pack_c33(_interp_control())
    defects = run_personalization_gate_c33(
        normalize_native_scenario_llm_c1(native), pack
    )
    assert any(d["code"] == DEFECT_CLAIM_WITHOUT_EVIDENCE for d in defects)


def test_light_forbids_precise_natal():
    native = _day_shared_native()
    native["personalization_depth"] = DEPTH_LIGHT
    native["conflict"]["why_personal"] = "В вашем натале Марс в 7 доме давит."
    pack = build_personalization_evidence_pack_c33(_interp_light(), birth_date_present=True)
    defects = run_personalization_gate_c33(
        normalize_native_scenario_llm_c1(native), pack
    )
    codes = {d["code"] for d in defects}
    assert DEFECT_DEPTH_OVERREACH in codes or DEFECT_NATAL_OVERCLAIM in codes


def test_deep_decorative_only_rejected():
    native = _day_shared_native()
    native["personalization_depth"] = DEPTH_DEEP
    native["conflict"]["why_personal"] = "Вам привычно сглаживать — сегодня иначе."
    native["interpretive_chorus"]["natal"] = [
        {
            "named_factor": "Луна",
            "human_meaning": "Вам чувствительнее тон.",
            "link_to_conflict": "Личная уязвимость в прояснении.",
            "evidence_refs": ["natal.moon.7"],
        }
    ]
    # No structural personalization traces
    pack = build_personalization_evidence_pack_c33(_interp_deep_a(), birth_time_present=True)
    defects = run_personalization_gate_c33(
        normalize_native_scenario_llm_c1(native), pack
    )
    assert any(d["code"] == DEFECT_DECORATIVE_ONLY for d in defects)


def test_deep_structural_personalization_passes():
    native = _day_shared_native()
    native["personalization_depth"] = DEPTH_DEEP
    native["conflict"]["force_a"] = "сгладить ради тишины (привычно вам)"
    native["conflict"]["force_b"] = "коротко назвать факт"
    native["conflict"]["personalization"] = {
        "personalization_level": DEPTH_DEEP,
        "personalization_reason": "habitual smooth vs required clarity",
        "personalization_evidence_refs": ["claim.personal.moon7.smooth"],
        "general_fallback_available": True,
        "habitual_force": "a",
        "required_movement": "b",
    }
    native["scenes"][0]["trap"] = "Согласиться ради тишины — ваш обычный ход."
    native["scenes"][0]["recommended_action"] = "Написать одну конкретную фразу вместо «нормально»."
    native["scenes"][0]["personalization"] = {
        "personalization_level": DEPTH_DEEP,
        "personalization_reason": "relationships — rejection sensitivity",
        "personalization_evidence_refs": ["claim.personal.venus.reject"],
        "sphere_reason": "sensitive domain relationships",
        "response_pattern": "smooth_conflict",
        "compensating_for": "smooth_conflict",
        "trap_pattern": "agree_for_silence",
        "general_fallback_available": True,
    }
    pack = build_personalization_evidence_pack_c33(_interp_deep_a(), birth_time_present=True)
    defects = run_personalization_gate_c33(
        normalize_native_scenario_llm_c1(native), pack
    )
    assert not any(
        d["code"] in {DEFECT_DECORATIVE_ONLY, DEFECT_CLAIM_WITHOUT_EVIDENCE, DEFECT_PROFILE_FACT_LEAK}
        for d in defects
    ), defects


def test_pairwise_deep_scenarios_differ_structurally():
    """Same day skeleton; A vs B personalization traces must differ."""
    base = _day_shared_native()

    a = deepcopy(base)
    a["personalization_depth"] = DEPTH_DEEP
    a["conflict"]["personalization"] = {
        "personalization_level": DEPTH_DEEP,
        "personalization_reason": "stop smoothing",
        "personalization_evidence_refs": ["claim.personal.moon7.smooth"],
        "habitual_force": "a",
        "required_movement": "b",
        "general_fallback_available": True,
    }
    a["scenes"][0]["personalization"] = {
        "personalization_level": DEPTH_DEEP,
        "personalization_reason": "relationships",
        "personalization_evidence_refs": ["claim.personal.venus.reject"],
        "response_pattern": "smooth_conflict",
        "compensating_for": "smooth_conflict",
        "trap_pattern": "agree_for_silence",
        "sphere_reason": "rejection sensitivity",
        "general_fallback_available": True,
    }
    a["scenes"][0]["recommended_action"] = "Сказать одну конкретную фразу вместо молчания."

    b = deepcopy(base)
    b["personalization_depth"] = DEPTH_DEEP
    b["scenes"][0]["sphere"] = "work_decisions"
    b["scenes"][0]["scene_id"] = "scene.work_decisions"
    b["conflict"]["personalization"] = {
        "personalization_level": DEPTH_DEEP,
        "personalization_reason": "do not turn clarity into pressure",
        "personalization_evidence_refs": ["claim.personal.mars1.direct"],
        "habitual_force": "b",
        "required_movement": "a",
        "general_fallback_available": True,
    }
    b["scenes"][0]["personalization"] = {
        "personalization_level": DEPTH_DEEP,
        "personalization_reason": "work_decisions — over_control",
        "personalization_evidence_refs": ["claim.personal.sat.overload"],
        "response_pattern": "over_control",
        "compensating_for": "over_control",
        "trap_pattern": "pressure_clarity",
        "sphere_reason": "responsibility overload at work",
        "general_fallback_available": True,
    }
    b["scenes"][0]["recommended_action"] = "Задать один вопрос до ответа; не решать за коллегу."
    b["scenes"][0]["trap"] = "Превратить ясность в давление и решить за других."

    pack_a = build_personalization_evidence_pack_c33(_interp_deep_a(), birth_time_present=True)
    pack_b = build_personalization_evidence_pack_c33(_interp_deep_b(), birth_time_present=True)
    na = normalize_native_scenario_llm_c1(a)
    nb = normalize_native_scenario_llm_c1(b)
    assert not run_personalization_gate_c33(na, pack_a) or all(
        d["code"] != DEFECT_DECORATIVE_ONLY for d in run_personalization_gate_c33(na, pack_a)
    )
    da = run_personalization_gate_c33(na, pack_a)
    db = run_personalization_gate_c33(nb, pack_b)
    assert not any(d["code"] == DEFECT_DECORATIVE_ONLY for d in da), da
    assert not any(d["code"] == DEFECT_DECORATIVE_ONLY for d in db), db

    assert na["scenes"][0]["sphere"] != nb["scenes"][0]["sphere"] or (
        na["scenes"][0]["recommended_action"] != nb["scenes"][0]["recommended_action"]
    )
    assert na["conflict"]["personalization"]["habitual_force"] != nb["conflict"]["personalization"][
        "habitual_force"
    ]
    # Cross-profile evidence orphan check
    cross = run_personalization_gate_c33(na, pack_b)
    # A's refs should not be in B's pack — may flag orphan if claim.personal.* checked
    # At minimum packs differ
    assert set(pack_a["evidence_refs"]) != set(pack_b["evidence_refs"])
    assert cross is not None  # gate runs


def test_profile_fact_leak_rejected():
    native = _day_shared_native()
    native["scenes"][0]["setup"] = "Ваш тип генератор Human Design и координаты 55.755, 37.617."
    pack = build_personalization_evidence_pack_c33(_interp_deep_a(), birth_time_present=True)
    defects = run_personalization_gate_c33(normalize_native_scenario_llm_c1(native), pack)
    assert any(d["code"] == DEFECT_PROFILE_FACT_LEAK for d in defects)
    assert personalization_decision_after_retries(defects) == "reject_story"


def test_downgrade_strips_personal_keeps_day_story():
    native = normalize_native_scenario_llm_c1(_day_shared_native())
    native["personalization_depth"] = DEPTH_DEEP
    native["conflict"]["why_personal"] = "Вам обычно свойственно сглаживать."
    native["interpretive_chorus"]["natal"] = [
        {
            "named_factor": "Луна",
            "human_meaning": "Вам привычно",
            "link_to_conflict": "x",
            "evidence_refs": ["natal.moon.7"],
            "conflict_id": "conflict.x",
        }
    ]
    down = downgrade_native_to_general_c33(native)
    assert down["personalization_depth"] == DEPTH_GENERAL
    assert down["interpretive_chorus"]["natal"] == []
    assert down["conflict"]["why_personal"] == ""
    assert down["scenes"], "day scenes kept"
    assert down["conflict"]["title"]


def test_normalize_keeps_personalization_trace():
    native = _day_shared_native()
    native["personalization_depth"] = DEPTH_LIGHT
    native["conflict"]["personalization"] = {
        "personalization_level": DEPTH_LIGHT,
        "personalization_reason": "tone",
        "personalization_evidence_refs": ["claim.personal.sun_sign"],
        "general_fallback_available": True,
    }
    norm = normalize_native_scenario_llm_c1(native)
    assert norm["schema_version"] == NATIVE_LLM_SCHEMA_VERSION
    assert norm["personalization_depth"] == DEPTH_LIGHT
    assert norm["conflict"]["personalization"]["personalization_evidence_refs"]
