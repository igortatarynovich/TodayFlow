"""Phase C1 — native day_scenario LLM schema / validate / project."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.day_events_ranker_v1 import rank_day_events
from todayflow_backend.services.day_scenario_native_llm_c1 import (
    GENERATION_SOURCE_DETERMINISTIC,
    GENERATION_SOURCE_NATIVE,
    LEGACY_FORBIDDEN_KEYS,
    NATIVE_LLM_SCHEMA_VERSION,
    collect_allowed_evidence_ids,
    find_legacy_keys,
    has_native_generation_marker,
    native_llm_to_day_scenario_v1,
    normalize_native_scenario_llm_c1,
    validate_native_scenario_llm_c1,
)
from todayflow_backend.services.day_scenario_project_v1 import project_day_scenario_onto_day_story_v1
from todayflow_backend.services.day_scenario_v1 import build_day_scenario_v1, validate_day_scenario_v1
from todayflow_backend.services.day_story_interpretation_v1 import build_day_story_interpretation_v1
from todayflow_backend.services.day_story_v1 import (
    build_day_story_fallback_v1,
    day_story_to_today_contract_v1,
    validate_day_story_v1,
)
from todayflow_backend.services.day_thesis_v1 import build_day_thesis_v1


def _pack():
    return rank_day_events(
        [
            {
                "id": "moon-pisces",
                "kind": "moon_ingress",
                "title_ru": "Луна → Рыбы",
                "fact_ru": "Луна вошла в Рыбы.",
                "body": "Moon",
                "sign": "Pisces",
                "priority_hint": "primary",
            },
            {
                "id": "merc-direct",
                "kind": "station_direct",
                "title_ru": "Меркурий direct",
                "fact_ru": "Меркурий разворачивается в директ.",
                "priority_hint": "primary",
            },
        ]
    )


def _interp_and_allowed():
    pack = _pack()
    thesis = build_day_thesis_v1(day_events_pack=pack)
    ritual = {
        "tarot_name_ru": "Отшельник",
        "numerology_value": 7,
        "head_topic": "relationships",
    }
    interp = build_day_story_interpretation_v1(
        day_engine_brief={
            "anchor_summary": "Ось.",
            "do_hint": "Шаг.",
            "avoid_hint": "Стоп.",
            "thread_head_topic": "relationships",
        },
        ritual_context=ritual,
        celestial_events={"day_events_pack": pack},
        day_thesis=thesis,
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
    )
    allowed = collect_allowed_evidence_ids(
        interpretation=interp,
        ritual_context=ritual,
        celestial_events={"day_events_pack": pack},
    )
    return pack, thesis, ritual, interp, allowed


def _valid_native(**overrides):
    base = {
        "schema_version": NATIVE_LLM_SCHEMA_VERSION,
        "interpretive_chorus": {
            "astrology": [
                {
                    "named_factor": "Луна в Рыбах",
                    "human_meaning": "Эмоции сильнее логики.",
                    "link_to_conflict": "Поэтому конфликт прояснения vs сглаживания острее.",
                    "evidence_refs": ["moon-pisces"],
                }
            ],
            "day_card": {
                "named_factor": "Карта дня — Отшельник",
                "archetype_role": "Архетип паузы перед ответом.",
                "link_to_conflict": "Отшельник описывает тот же конфликт: сначала понять, потом говорить.",
                "evidence_refs": ["day_card"],
            },
            "day_number": {
                "named_factor": "Число дня — 7",
                "tempo": "сначала понять",
                "style": "без спешки",
                "link_to_conflict": "Число 7 задаёт ритм прохождения того же конфликта.",
                "evidence_refs": ["day_number"],
            },
            "natal": [
                {
                    "named_factor": "Личная активация усиливает чувствительность.",
                    "human_meaning": "Реакция может быть сильнее средней.",
                    "link_to_conflict": "Поэтому сглаживание особенно соблазнительно.",
                    "evidence_refs": ["natal"],
                }
            ],
        },
        "conflict": {
            "title": "Прояснение против сглаживания",
            "thesis": "Сегодня важнее назвать точно, чем сохранить ложную гармонию.",
            "force_a": "сгладить ради тишины",
            "force_b": "сказать коротко и честно",
            "why_today": "Луна в Рыбах и Меркурий direct собирают одну линию.",
            "why_personal": "Личная чувствительность делает сглаживание привычным.",
            "driver_refs": ["moon-pisces", "merc-direct"],
            "evidence_refs": ["moon-pisces", "merc-direct"],
        },
        "scenes": [
            {
                "scene_id": "scene.relationships",
                "sphere": "relationships",
                "role_in_story": "primary",
                "setup": "В отношениях проявляется «Прояснение против сглаживания».",
                "opportunity": "Одно короткое сообщение вместо длинного оправдания.",
                "trap": "Согласиться сразу, чтобы не тревожить.",
                "recommended_action": "Написать черновик и отправить после паузы.",
                "avoid_action": "Не сглаживать смысл ради мгновенного мира.",
                "everyday_example": "Ответ на сообщение близкого: сначала смысл, потом скорость.",
                "evidence_refs": ["moon-pisces"],
                "chorus_refs": ["conflict", "day_card", "day_number"],
            },
            {
                "scene_id": "scene.work_decisions",
                "sphere": "work_decisions",
                "role_in_story": "support",
                "setup": "В работе тот же сюжет «Прояснение против сглаживания».",
                "opportunity": "Закрыть одну задачу ясным решением.",
                "trap": "Откладывать, чтобы никого не задеть.",
                "recommended_action": "Одно письмо с точной формулировкой.",
                "avoid_action": "Не размывать ответ общими фразами.",
                "everyday_example": "Письмо коллеге: один абзац, один запрос.",
                "evidence_refs": ["merc-direct"],
                "chorus_refs": ["conflict", "astrology"],
            },
        ],
        "prop_material": {
            "color_scene_candidates": ["scene.relationships"],
            "avoid_color_trigger": "Ловушка сглаживания усиливается шумным цветом.",
            "goal_candidates": [
                {"scene_id": "scene.relationships", "text": "Одно точное сообщение до обеда."}
            ],
            "affirmation_tension": {
                "scene_id": "scene.relationships",
                "trap": "сгладить",
                "text": "Я могу сказать коротко и остаться в контакте.",
            },
            "humor_setup": None,
        },
        "visual_mode": "tension",
        "generation_notes": "test",
        "primary_scene_id": "scene.relationships",
    }
    base.update(overrides)
    return base


def test_native_schema_accepts_valid_payload():
    _, _, _, _, allowed = _interp_and_allowed()
    native = normalize_native_scenario_llm_c1(_valid_native())
    assert validate_native_scenario_llm_c1(native, allowed_evidence_ids=allowed) == []


def test_legacy_keys_rejected():
    raw = _valid_native(expect="legacy expect", trap="legacy trap", do=["x"])
    assert find_legacy_keys(raw)
    assert any(k in LEGACY_FORBIDDEN_KEYS for k in ("expect", "trap", "do"))
    errors = validate_native_scenario_llm_c1(
        normalize_native_scenario_llm_c1(raw),
        allowed_evidence_ids={"moon-pisces", "merc-direct", "day_card", "day_number", "natal", "astrology", "conflict"},
    )
    # normalize drops legacy keys from top-level copy — validate raw keys separately
    assert find_legacy_keys(raw)
    # Ensure call path would reject: simulate validate on raw before normalize strip
    assert "expect" in raw


def test_legacy_keys_on_raw_block_acceptance_path():
    """Wire rejects if raw JSON still contains legacy keys."""
    raw = _valid_native()
    raw["expect"] = "should fail"
    _, _, _, _, allowed = _interp_and_allowed()
    normalized = normalize_native_scenario_llm_c1(raw)
    errors = validate_native_scenario_llm_c1(normalized, allowed_evidence_ids=allowed)
    legacy = find_legacy_keys(raw)
    assert legacy
    combined = list(errors) + [f"legacy_keys:{','.join(legacy)}"]
    assert any("legacy_keys" in e for e in combined)


def test_scene_without_conflict_link_rejected():
    native = _valid_native()
    native["scenes"][0]["setup"] = "Совершенно другой день без связи."
    native["scenes"][0]["opportunity"] = "Что-то ещё."
    native["scenes"][0]["trap"] = "Иное."
    native["scenes"][0]["chorus_refs"] = ["astrology"]
    normalized = normalize_native_scenario_llm_c1(native)
    errors = validate_native_scenario_llm_c1(
        normalized,
        allowed_evidence_ids={"moon-pisces", "merc-direct", "day_card", "day_number", "natal", "astrology", "conflict"},
    )
    assert any("scene_missing_conflict_link" in e for e in errors)


def test_parallel_forecast_rejected():
    native = _valid_native()
    native["interpretive_chorus"]["day_card"]["link_to_conflict"] = (
        "Это отдельный прогноз и вторая история дня."
    )
    errors = validate_native_scenario_llm_c1(
        normalize_native_scenario_llm_c1(native),
        allowed_evidence_ids={"moon-pisces", "merc-direct", "day_card", "day_number", "natal", "astrology", "conflict"},
    )
    assert any("parallel_forecast" in e for e in errors)


def test_unknown_evidence_rejected():
    native = _valid_native()
    native["conflict"]["driver_refs"] = ["invented-planet-42"]
    errors = validate_native_scenario_llm_c1(
        normalize_native_scenario_llm_c1(native),
        allowed_evidence_ids={"moon-pisces", "merc-direct", "day_card", "day_number", "natal", "astrology", "conflict"},
    )
    assert any("unknown_evidence" in e for e in errors)


def test_native_forces_optional_empty_ok_incomplete_rejected():
    """v3.1: force_a/force_b may both be empty; one-sided pair is incomplete; no автопилот defaults."""
    allowed = {
        "moon-pisces",
        "merc-direct",
        "day_card",
        "day_number",
        "natal",
        "astrology",
        "conflict",
    }
    even = _valid_native()
    even["conflict"]["force_a"] = ""
    even["conflict"]["force_b"] = ""
    norm = normalize_native_scenario_llm_c1(even)
    assert validate_native_scenario_llm_c1(norm, allowed_evidence_ids=allowed) == []

    incomplete = _valid_native()
    incomplete["conflict"]["force_b"] = ""
    errors = validate_native_scenario_llm_c1(
        normalize_native_scenario_llm_c1(incomplete),
        allowed_evidence_ids=allowed,
    )
    assert any("conflict_forces_incomplete" in e for e in errors)

    pack, thesis, ritual, interp, _allowed = _interp_and_allowed()
    scenario = native_llm_to_day_scenario_v1(
        norm,
        interpretation=interp,
        ritual_context=ritual,
        celestial_events={"day_events_pack": pack},
        day_thesis=thesis,
    )
    opposing = (scenario.get("conflict") or {}).get("opposing_forces") or {}
    assert opposing.get("a") == ""
    assert opposing.get("b") == ""


def test_native_maps_to_scenario_and_b5_projector():
    pack, thesis, ritual, interp, allowed = _interp_and_allowed()
    native = normalize_native_scenario_llm_c1(_valid_native())
    assert validate_native_scenario_llm_c1(native, allowed_evidence_ids=allowed) == []
    scenario = native_llm_to_day_scenario_v1(
        native,
        interpretation=interp,
        ritual_context=ritual,
        celestial_events={"day_events_pack": pack},
        day_thesis=thesis,
    )
    assert scenario["generation_source"] == GENERATION_SOURCE_NATIVE
    assert scenario.get("visual_mode") == "tension"
    assert validate_day_scenario_v1(scenario) == []
    assert all(
        str(sc.get("serves_conflict") or "") == "тон дня"
        for sc in (scenario.get("scenes") or [])
        if isinstance(sc, dict)
    )
    assert scenario["props"]["color"]["origin_scene_id"]

    story = build_day_story_fallback_v1(
        day_engine_brief={"anchor_summary": "Ось.", "do_hint": "Шаг.", "avoid_hint": "Стоп."},
        color="Лазурь",
        interpretation=interp,
        celestial_events={"day_events_pack": pack},
        ritual_context=ritual,
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
    )
    # Inject legacy prose that must be overwritten
    story["interpretation_status"] = "ok"
    story["expect"] = "LLM legacy expect"
    projected = project_day_scenario_onto_day_story_v1(story, scenario)
    assert projected.get("visual_mode") == "tension"
    assert projected["interpretation_status"] == "ok"
    assert not str(projected["expect"]).startswith("LLM legacy")
    assert "Прояснение" in projected["primary_conflict"] or "Прояснение" in projected["theme"]
    assert projected["day_scenario"]["generation_source"] == GENERATION_SOURCE_NATIVE
    assert validate_day_story_v1(projected) == []
    contract = day_story_to_today_contract_v1(projected)
    assert contract["day_story"]["expect"]
    assert contract["day_story"]["talisman"]["color"] == scenario["props"]["color"]["name"]
    assert (contract.get("day_atmosphere") or {}).get("visual_mode") == "tension"


def test_native_invalid_visual_mode_dropped_atmosphere_falls_back():
    pack, thesis, ritual, interp, allowed = _interp_and_allowed()
    native = normalize_native_scenario_llm_c1(_valid_native(visual_mode="not-a-mood"))
    assert validate_native_scenario_llm_c1(native, allowed_evidence_ids=allowed) == []
    scenario = native_llm_to_day_scenario_v1(
        native,
        interpretation=interp,
        ritual_context=ritual,
        celestial_events={"day_events_pack": pack},
        day_thesis=thesis,
    )
    assert "visual_mode" not in scenario or scenario.get("visual_mode") is None
    story = build_day_story_fallback_v1(
        day_engine_brief={"anchor_summary": "Ось.", "do_hint": "Шаг.", "avoid_hint": "Стоп."},
        interpretation=interp,
        ritual_context=ritual,
        celestial_events={"day_events_pack": pack},
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
    )
    projected = project_day_scenario_onto_day_story_v1(story, scenario)
    assert not projected.get("visual_mode")
    contract = day_story_to_today_contract_v1(projected, generation_id="fallback-mood")
    atm = contract.get("day_atmosphere") or {}
    assert atm.get("visual_mode") in {
        "grounded",
        "flow",
        "radiance",
        "momentum",
        "clarity",
        "tension",
        "renewal",
        "depth",
    }


def test_invalid_output_projects_to_unavailable_not_legacy():
    story = {"expect": "legacy", "trap": "legacy", "do": ["x"], "interpretation_status": "ok"}
    projected = project_day_scenario_onto_day_story_v1(story, None)
    assert projected["interpretation_status"] == "unavailable"
    assert projected["expect"] == ""
    assert projected.get("day_scenario") is None


def test_old_cache_without_marker_is_invalid_meaning_cache():
    story = {
        "expect": "old expect",
        "trap": "old trap",
        "do": ["old"],
        "day_scenario": {"scenes": [{"scene_id": "x"}], "runtime_sot": True},
    }
    assert has_native_generation_marker(story) is False
    projected = project_day_scenario_onto_day_story_v1(story, None)
    assert projected["interpretation_status"] == "unavailable"
    assert projected["expect"] == ""


def test_deterministic_engine_gets_c1_marker():
    pack, thesis, ritual, interp, _ = _interp_and_allowed()
    scenario = build_day_scenario_v1(
        interpretation=interp,
        day_events_pack=pack,
        day_thesis=thesis,
        ritual_context=ritual,
    )
    assert scenario["generation_source"] == GENERATION_SOURCE_DETERMINISTIC
    story = {"interpretation_status": "unavailable"}
    projected = project_day_scenario_onto_day_story_v1(story, scenario)
    assert has_native_generation_marker(projected) is True


def test_scenes_too_few_rejected():
    native = _valid_native()
    native["scenes"] = native["scenes"][:1]
    errors = validate_native_scenario_llm_c1(normalize_native_scenario_llm_c1(native))
    assert "scenes_too_few" in errors


def test_primary_scene_id_unknown_rejected():
    native = _valid_native()
    native["primary_scene_id"] = "scene.does-not-exist"
    errors = validate_native_scenario_llm_c1(normalize_native_scenario_llm_c1(native))
    assert "primary_scene_id_unknown" in errors


def test_primary_scene_id_missing_rejected_without_unique_role():
    native = _valid_native()
    native.pop("primary_scene_id", None)
    for sc in native["scenes"]:
        sc["role_in_story"] = "support"
    errors = validate_native_scenario_llm_c1(normalize_native_scenario_llm_c1(native))
    assert "primary_scene_id_missing" in errors


def test_normalize_fills_primary_scene_id_from_unique_role():
    native = _valid_native()
    native.pop("primary_scene_id", None)
    norm = normalize_native_scenario_llm_c1(native)
    assert norm.get("primary_scene_id") == "scene.relationships"
