"""Tests for day_scenario_v1 — B1 engine (foundation, chorus, conflict, scenes)."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.day_events_ranker_v1 import rank_day_events
from todayflow_backend.services.day_scenario_v1 import (
    DAY_SCENARIO_V1_CONTRACT,
    build_day_scenario_v1,
    build_interpretive_chorus_v1,
    build_scenario_conflict_v1,
    build_scenario_foundation_v1,
    validate_day_scenario_v1,
)
from todayflow_backend.services.day_story_interpretation_v1 import build_day_story_interpretation_v1
from todayflow_backend.services.day_thesis_v1 import build_day_thesis_v1


def _pack_merc_moon():
    return rank_day_events(
        [
            {
                "id": "merc-direct",
                "kind": "station_direct",
                "title_ru": "Меркурий разворачивается в директ",
                "fact_ru": "Меркурий разворачивается в директное движение.",
                "body": "Mercury",
                "priority_hint": "primary",
            },
            {
                "id": "moon-pisces",
                "kind": "moon_ingress",
                "title_ru": "Луна → Рыбы",
                "fact_ru": "Луна вошла в Рыбы.",
                "body": "Moon",
                "sign": "Pisces",
                "priority_hint": "primary",
            },
        ]
    )


def test_scenario_builds_one_conflict_from_drivers_not_card_alone():
    pack = _pack_merc_moon()
    thesis = build_day_thesis_v1(day_events_pack=pack)
    ritual = {
        "tarot_name_ru": "Отшельник",
        "tarot_main_id": "09",
        "numerology_value": 7,
        "head_topic": "relationships",
    }
    interp = build_day_story_interpretation_v1(
        day_engine_brief={
            "anchor_summary": "Ось дня — ясность без сглаживания.",
            "do_hint": "Сказать прямо.",
            "avoid_hint": "Не соглашаться сразу.",
            "thread_head_topic": "relationships",
        },
        ritual_context=ritual,
        celestial_events={"day_events_pack": pack, "lunar_phase": {"name": "Растущая луна"}},
        day_thesis=thesis,
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
    )
    scenario = build_day_scenario_v1(
        interpretation=interp,
        day_events_pack=pack,
        day_thesis=thesis,
        ritual_context=ritual,
    )
    assert scenario["contract_version"] == DAY_SCENARIO_V1_CONTRACT
    assert scenario["runtime_sot"] is True
    assert validate_day_scenario_v1(scenario) == []

    conflict = scenario["conflict"]
    assert conflict["short_name"]
    assert "…" not in conflict["short_name"]
    assert " — пока " not in conflict["short_name"]
    assert conflict["driver_ids"]
    assert "merc-direct" in conflict["driver_ids"] or "moon-pisces" in conflict["driver_ids"]
    assert conflict["opposing_forces"]["a"]
    assert conflict["opposing_forces"]["b"]
    assert "day_card" in conflict["chorus_references"]
    assert "day_number" in conflict["chorus_references"]

    # Card/number explain, do not replace drivers
    foundation = scenario["foundation"]
    assert foundation["tarot_card"]["name"] == "Отшельник"
    assert foundation["day_number"]["value"] == 7
    assert foundation["ranked_drivers"]


def test_short_name_is_tension_only_not_mashed_truncated_fact():
    from todayflow_backend.services.day_scenario_v1 import (
        _everyday_conflict_short_name,
        sanitize_conflict_short_name,
    )

    name = _everyday_conflict_short_name(
        force_a="удержать привычное",
        force_b="принять поворот",
        lead_fact="Связь Солнца и Марса описывает, как ты идёшь к цели сразу после искры; это мотор напора и риска.",
        registry_label="Перемены",
    )
    assert name == "Удержать привычное или принять поворот"
    assert "…" not in name
    healed = sanitize_conflict_short_name(
        "Удержать привычное или принять поворот — пока связь Солнца и Марса описывает, как ты идёшь к це…"
    )
    assert healed == "Удержать привычное или принять поворот"
    cal = sanitize_conflict_short_name(
        "Ломать работающее или беречь ровный ритм — пока календарный день 2026-07-28 — 209-й день года."
    )
    assert cal == "Ломать работающее или беречь ровный ритм"
    assert "календар" not in cal.lower()


def test_kitchen_firdaria_not_in_why_personal_or_chorus():
    pack = _pack_merc_moon()
    thesis = build_day_thesis_v1(day_events_pack=pack)
    foundation = build_scenario_foundation_v1(
        day_events_pack=pack,
        ritual_context={"tarot_name_ru": "Отшельник", "numerology_value": 7},
    )
    foundation["personal_natal_activations"] = [
        {
            "id": "claim.personal.astro.time-lords",
            "text": (
                "Firdaria: мажор Луна (2021-02-12 → 2030-02-12), субпериод Солнце "
                "(до 2027-08-19). ZR Fortune→Весы: L1 Козерог/Сатурн. Лоты soft: Луна/Солнце (нет ASC)."
            ),
            "evidence_ids": ["personal_astrology.time_lords"],
            "layer": "personal_astrology",
        }
    ]
    conflict = build_scenario_conflict_v1(foundation=foundation, day_thesis=thesis)
    assert "Firdaria" not in conflict["why_personal"]
    assert "ZR Fortune" not in conflict["why_personal"]
    chorus = build_interpretive_chorus_v1(
        foundation=foundation,
        conflict_label=conflict["short_name"],
    )
    for row in chorus.get("natal") or []:
        assert "Firdaria" not in str(row.get("named_factor") or "")
        assert "ZR Fortune" not in str(row.get("named_factor") or "")


def test_chorus_names_moon_card_number():
    pack = _pack_merc_moon()
    thesis = build_day_thesis_v1(day_events_pack=pack)
    foundation = build_scenario_foundation_v1(
        day_events_pack=pack,
        ritual_context={"tarot_name_ru": "Отшельник", "numerology_value": 7},
    )
    conflict = build_scenario_conflict_v1(foundation=foundation, day_thesis=thesis)
    chorus = build_interpretive_chorus_v1(
        foundation=foundation,
        conflict_label=conflict["short_name"],
    )
    astro_blob = " ".join(v.get("named_factor") or "" for v in chorus["astrology"])
    assert "Рыб" in astro_blob or "Меркурий" in astro_blob or "Луна" in astro_blob
    assert chorus["day_card"]["named_factor"].startswith("Карта дня")
    assert "Отшельник" in chorus["day_card"]["named_factor"]
    assert chorus["day_card"]["must_not_invent_second_plot"] is True
    assert chorus["day_number"]["named_factor"].startswith("Число дня")
    assert chorus["day_number"]["tempo"]  # 7 → глубина
    assert chorus["parallel_forecast_forbidden"] is True


def test_scenes_are_relevant_and_serve_conflict():
    pack = _pack_merc_moon()
    thesis = build_day_thesis_v1(day_events_pack=pack)
    ritual = {"tarot_name_ru": "Отшельник", "numerology_value": 7, "head_topic": "relationships"}
    interp = build_day_story_interpretation_v1(
        day_engine_brief={
            "anchor_summary": "Ось.",
            "do_hint": "Шаг.",
            "avoid_hint": "Не спеши.",
            "thread_head_topic": "relationships",
        },
        ritual_context=ritual,
        celestial_events={"day_events_pack": pack},
        day_thesis=thesis,
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
    )
    scenario = build_day_scenario_v1(
        interpretation=interp,
        day_events_pack=pack,
        day_thesis=thesis,
        ritual_context=ritual,
    )
    scenes = scenario["scenes"]
    assert 1 <= len(scenes) <= 4
    labels = {s["serves_conflict"] for s in scenes}
    assert labels == {scenario["conflict"]["short_name"]}
    spheres = {s["sphere"] for s in scenes}
    # relationships topic should pull relationship/communication spheres
    assert spheres & {"relationships", "communication", "work_decisions"}
    for s in scenes:
        assert s["scene_id"].startswith("scene.")
        assert s["opportunity"]
        assert s["trap"]
        assert s["chorus_references"]


def test_props_from_scenes_have_origin_and_conflict_link():
    pack = _pack_merc_moon()
    thesis = build_day_thesis_v1(day_events_pack=pack)
    ritual = {
        "tarot_name_ru": "Отшельник",
        "numerology_value": 7,
        "head_topic": "relationships",
    }
    interp = build_day_story_interpretation_v1(
        day_engine_brief={
            "anchor_summary": "Ось дня.",
            "do_hint": "Сказать прямо.",
            "avoid_hint": "Не соглашаться сразу ради гармонии.",
            "thread_head_topic": "relationships",
        },
        ritual_context=ritual,
        celestial_events={"day_events_pack": pack},
        day_thesis=thesis,
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
    )
    scenario = build_day_scenario_v1(
        interpretation=interp,
        day_events_pack=pack,
        day_thesis=thesis,
        ritual_context=ritual,
    )
    assert validate_day_scenario_v1(scenario) == []
    props = scenario["props"]
    assert props["status"] == "ok"
    color = props["color"]
    assert color["origin_scene_id"]
    assert color["link_to_conflict"]
    assert color["so_t_note"].startswith("scenario_scene_derived")
    assert props["avoid_color"]["amplifies_trap"]
    assert props["avoid_color"]["origin_scene_id"] == color["origin_scene_id"]
    assert 1 <= len(props["goals"]) <= 3
    assert all(g.get("origin_scene_id") for g in props["goals"])
    assert props["affirmations"][0]["origin_scene_id"]
    assert props["affirmations"][0]["universal_formula"] is False
    assert props["strong_spheres"]
    # Catalog is knowledge — user why must mention today's forces, not only catalog benefit
    force_a = scenario["conflict"]["opposing_forces"]["a"]
    force_b = scenario["conflict"]["opposing_forces"]["b"]
    link = color["link_to_conflict"].lower()
    assert force_a in link or force_b in link or scenario["conflict"]["short_name"].lower() in link


def test_validate_rejects_empty_conflict_name():
    pack = _pack_merc_moon()
    scenario = build_day_scenario_v1(day_events_pack=pack)
    scenario["conflict"]["short_name"] = ""
    assert "conflict_missing_short_name" in validate_day_scenario_v1(scenario)


def test_scene_copy_varies_by_sphere_and_uses_name():
    pack = _pack_merc_moon()
    thesis = build_day_thesis_v1(day_events_pack=pack)
    ritual = {
        "tarot_name_ru": "Отшельник",
        "numerology_value": 7,
        "head_topic": "relationships",
    }
    interp = build_day_story_interpretation_v1(
        day_engine_brief={
            "anchor_summary": "Ось дня — ясность.",
            "do_hint": "Сказать прямо.",
            "avoid_hint": "Не сглаживать.",
            "thread_head_topic": "relationships",
        },
        ritual_context=ritual,
        celestial_events={"day_events_pack": pack},
        day_thesis=thesis,
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
    )
    scenario = build_day_scenario_v1(
        interpretation=interp,
        day_events_pack=pack,
        day_thesis=thesis,
        ritual_context=ritual,
        person_name="Игорь",
    )
    scenes = scenario["scenes"]
    assert scenes
    whats = [s["what_happens"] for s in scenes]
    opps = [s["opportunity"] for s in scenes]
    assert any(w.startswith("Игорь,") for w in whats)
    assert not any("тот же выбор — «" in w for w in whats)
    assert not any("день упирается в выбор: «" in w for w in whats)
    assert not any(o.startswith("Шанс выбрать «") for o in opps)
    assert len(set(opps)) == len(opps) or len(opps) == 1
    # No force-quote spam of opposing_forces across all scene lines
    force_a = scenario["conflict"]["opposing_forces"]["a"]
    force_b = scenario["conflict"]["opposing_forces"]["b"]
    joined = " ".join(
        f"{s.get('what_happens')} {s.get('opportunity')} {s.get('trap')}" for s in scenes
    )
    assert joined.count(f"«{force_a}»") <= 1
    assert joined.count(f"«{force_b}»") <= 1


def test_color_catalog_is_knowledge_not_sot():
    from todayflow_backend.services.day_color_catalog_v1 import (
        LAYER_B_PRIMARY_TAGS,
        PENDING_LAYER_B_COLORS,
        list_color_knowledge,
        validate_color_catalog_v1,
    )
    from todayflow_backend.services.day_scenario_v1 import _needed_color_tags

    rows = list_color_knowledge()
    assert len(rows) == 19  # 8 core + 6 layer-A + 5 layer-B (Champagne held)
    assert all("tags" in r and "name" in r and "symbolic_property" in r for r in rows)
    assert validate_color_catalog_v1() == []
    names = {str(r["name"]) for r in rows}
    assert {
        "Малахитовый",
        "Пыльная роза",
        "Мускатный",
        "Аметистовый",
        "Кобальтовый",
        "Слоновая кость",
    } <= names
    assert {
        "Шафрановый",
        "Терракотовый",
        "Гранатовый",
        "Хризолитовый",
        "Дымчато-сиреневый",
    } <= names
    # Champagne: no favorable-outcome signal in conflict — must stay pending
    assert names.isdisjoint(PENDING_LAYER_B_COLORS)
    assert "Шампань" not in names

    # Layer-B primary tags must be reachable from generator (anti-orphan)
    probes = [
        _needed_color_tags(trap="", force_a="", sphere="creativity", mode=""),
        _needed_color_tags(trap="", force_a="", sphere="home", mode=""),
        _needed_color_tags(trap="", force_a="", sphere="money", mode=""),
        _needed_color_tags(trap="страсть и желание", force_a="", sphere="relationships", mode=""),
        _needed_color_tags(trap="отпустить тему и завершить", force_a="", sphere="home", mode=""),
    ]
    reachable = set().union(*probes)
    assert LAYER_B_PRIMARY_TAGS <= reachable

    # «отпуск» / rest_travel must NOT fire gentle_closure (false positive guard)
    vacation = _needed_color_tags(
        trap="хочется в отпуск на море",
        force_a="",
        sphere="rest_travel",
        mode="recovery",
    )
    assert "gentle_closure" not in vacation
    assert "honor_loss" not in vacation
    # Verb form must fire closure
    release = _needed_color_tags(
        trap="пора отпустить старую обиду",
        force_a="",
        sphere="relationships",
        mode="",
    )
    assert {"gentle_closure", "honor_loss"} <= release


def test_layer_b_colors_win_scoring_on_their_triggers():
    from todayflow_backend.services.day_color_catalog_v1 import (
        get_color_entry,
        list_color_knowledge,
        score_color_for_needs,
    )
    from todayflow_backend.services.day_scenario_v1 import _needed_color_tags

    cases = [
        ("creativity", "", "Шафрановый"),
        ("home", "", "Терракотовый"),
        ("money", "", "Хризолитовый"),
        ("relationships", "страсть и желание", "Гранатовый"),
        # relationships (not home) so closure specialty is not tied with Терракотовый
        ("relationships", "пора отпустить и завершить", "Дымчато-сиреневый"),
    ]
    catalog = list_color_knowledge()
    for sphere, trap, expected in cases:
        needed = _needed_color_tags(trap=trap, force_a="", sphere=sphere, mode="")
        ranked = sorted(
            catalog,
            key=lambda e: score_color_for_needs(e, needed),
            reverse=True,
        )
        assert ranked[0]["name"] == expected, (sphere, trap, ranked[0]["name"], needed)
        assert get_color_entry(expected) is not None


def test_celestial_daily_symbol_presets_use_catalog_colors_only():
    """Legacy seed path must not reintroduce orphan color names outside COLOR_CATALOG_V1."""
    from todayflow_backend.services.celestial_events_builder import (
        _DAILY_SYMBOL_PRESETS,
        _build_color_symbol,
    )
    from todayflow_backend.services.day_color_catalog_v1 import COLOR_CATALOG_V1

    canon = {str(r["name"]) for r in COLOR_CATALOG_V1}
    orphans = {"Перламутровый", "Сливовый", "Песочный", "Серебряный"}
    preset_colors = {p["color"] for p in _DAILY_SYMBOL_PRESETS}
    assert not (preset_colors & orphans)
    assert preset_colors <= canon
    for name in canon:
        sym = _build_color_symbol(name)
        assert sym["benefit_ru"]
        assert sym["name"] == name
    # Unknown name: no invented calm prose
    empty = _build_color_symbol("Перламутровый")
    assert empty["benefit_ru"] == ""
    assert empty["clothing_ru"] == ""


def test_conflict_driver_ids_prefer_natal_pt_over_pack():
    """Wave 2 D.2b: when personal_natal_activations has pt-*, those become conflict.driver_ids."""
    pack = _pack_merc_moon()
    thesis = build_day_thesis_v1(day_events_pack=pack)
    foundation = build_scenario_foundation_v1(
        day_events_pack=pack,
        ritual_context={"tarot_name_ru": "Отшельник", "numerology_value": 7},
    )
    foundation["personal_natal_activations"] = [
        {
            "id": "pt-mars-square-sun",
            "rank": 1,
            "text": "Марс давит",
            "evidence_ids": ["pt-mars-square-sun"],
            "layer": "personal",
        },
        {
            "id": "pt-venus-trine-moon",
            "rank": 2,
            "text": "Венера мягче",
            "evidence_ids": ["pt-venus-trine-moon"],
            "layer": "personal",
        },
    ]
    conflict = build_scenario_conflict_v1(foundation=foundation, day_thesis=thesis)
    assert conflict["driver_ids"] == ["pt-mars-square-sun", "pt-venus-trine-moon"]
    # Pack evidence remains on foundation for dramaturgy provenance
    pack_ids = [d["id"] for d in foundation["ranked_drivers"] if isinstance(d, dict) and d.get("id")]
    assert pack_ids
    assert conflict["driver_ids"] != pack_ids[:2]
