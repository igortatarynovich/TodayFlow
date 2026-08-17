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
    find_verbatim_seed_leaks_v1,
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
    # Deterministic build has no meaning scenes until native LLM (B5).
    assert "scenes_empty" in validate_day_scenario_v1(scenario)

    conflict = scenario["conflict"]
    assert conflict["short_name"]
    assert "…" not in conflict["short_name"]
    assert " — пока " not in conflict["short_name"]
    assert conflict["driver_ids"]
    assert "merc-direct" in conflict["driver_ids"] or "moon-pisces" in conflict["driver_ids"]
    # v3.1: opposing_forces may be empty — not invented from family/mode bank
    forces = conflict.get("opposing_forces") or {}
    assert isinstance(forces, dict)
    assert "day_card" in conflict["chorus_references"]
    assert "day_number" in conflict["chorus_references"]

    # Card/number explain, do not replace drivers
    foundation = scenario["foundation"]
    assert foundation["tarot_card"]["name"] == "Отшельник"
    assert foundation["day_number"]["value"] == 7
    assert foundation["ranked_drivers"]


def test_short_name_prefers_forces_then_registry_never_raw_sky_fact():
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
    even = _everyday_conflict_short_name(
        force_a="",
        force_b="",
        lead_fact="Меркурий разворачивается в директное движение.",
        registry_label="Перемены",
        mode="stability",
    )
    assert "или" not in even.lower()
    assert "меркурий" not in even.lower()
    assert "перемен" in even.lower()
    sky_only = _everyday_conflict_short_name(
        force_a="",
        force_b="",
        lead_fact="Меркурий разворачивается в директное движение.",
        registry_label="",
        mode="stability",
    )
    assert sky_only == "Ровный темп дня"
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
    # Deterministic bank retired — no invented scene meaning without native LLM.
    assert scenario["scenes"] == []
    assert "scenes_empty" in validate_day_scenario_v1(scenario)
    short = scenario["conflict"]["short_name"]
    assert "меркурий" not in short.lower()
    assert "разворач" not in short.lower()


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
    from todayflow_backend.services.day_scenario_v1 import build_scenario_props_v1

    scenes = [
        {
            "scene_id": "scene.relationships",
            "sphere": "relationships",
            "sphere_label_ru": "Отношения",
            "role_in_story": "primary",
            "what_happens": "В близком контакте сегодня важна одна честная фраза.",
            "why": "",
            "opportunity": "Одна фраза вслух — без сглаживания.",
            "trap": "Снова сгладить ради тишины.",
            "recommended_action": "Назови одну вещь прямо.",
            "do_not": "Не делай вид, что всё нормально.",
            "domestic_example": "Короткий разговор.",
            "evidence_references": list(scenario["conflict"].get("driver_ids") or []),
            "chorus_references": ["conflict"],
            "confidence": 0.7,
            "serves_conflict": "тон дня",
        }
    ]
    scenario["scenes"] = scenes
    scenario["props"] = build_scenario_props_v1(
        conflict=scenario["conflict"],
        scenes=scenes,
        chorus=scenario["chorus"],
        day_favorable=False,
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
    force_a = (scenario["conflict"].get("opposing_forces") or {}).get("a") or ""
    force_b = (scenario["conflict"].get("opposing_forces") or {}).get("b") or ""
    link = color["link_to_conflict"].lower()
    if force_a:
        assert force_a.lower() not in link
    if force_b:
        assert force_b.lower() not in link
    assert isinstance(color["link_to_conflict"], str) and len(color["link_to_conflict"].strip()) > 8
    effect = str(color.get("expected_effect_today") or "")
    assert effect and color["link_to_conflict"] not in effect


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
    # Deterministic path does not invent sphere beat copy (native LLM only).
    assert scenario["scenes"] == []
    assert "scenes_empty" in validate_day_scenario_v1(scenario)


def test_chorus_and_scenes_do_not_paste_short_name_seed():
    """v3.1 seed-kill: short_name / A|B must not seed chorus link_to_conflict or scene why."""
    from todayflow_backend.services.day_scenario_v1 import build_scenario_scenes_v1

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
    foundation = build_scenario_foundation_v1(
        day_events_pack=pack,
        ritual_context=ritual,
        interpretation=interp,
    )
    conflict = build_scenario_conflict_v1(
        foundation=foundation,
        day_thesis=thesis,
        interpretation=interp,
    )
    # Inject a classic binary seed as if an old cache / LLM pasted it
    conflict = {
        **conflict,
        "short_name": "Тащить старое или отпустить и восстановиться",
        "opposing_forces": {"a": "тащить старое", "b": "отпустить и восстановиться"},
    }
    chorus = build_interpretive_chorus_v1(
        foundation=foundation,
        conflict_label=conflict["short_name"],
        interpretation=interp,
    )
    seed = conflict["short_name"]
    force_a = conflict["opposing_forces"]["a"]
    force_b = conflict["opposing_forces"]["b"]
    blobs: list[str] = []
    for row in chorus.get("astrology") or []:
        if isinstance(row, dict):
            blobs.append(f"{row.get('human_meaning')} {row.get('link_to_conflict')}")
    card = chorus.get("day_card") or {}
    if isinstance(card, dict):
        blobs.append(
            f"{card.get('link_to_conflict')} {card.get('archetype_role')} {card.get('human_meaning')}"
        )
    number = chorus.get("day_number") or {}
    if isinstance(number, dict):
        blobs.append(f"{number.get('link_to_conflict')} {number.get('human_meaning')}")
    for row in chorus.get("natal") or []:
        if isinstance(row, dict):
            blobs.append(f"{row.get('human_meaning')} {row.get('link_to_conflict')}")
    joined_chorus = " ".join(blobs)
    assert seed not in joined_chorus
    assert f"«{force_a}»" not in joined_chorus
    assert f"«{force_b}»" not in joined_chorus
    assert f"«{seed}»" not in joined_chorus
    assert "ощутимый фон дня" not in joined_chorus

    scenes = build_scenario_scenes_v1(
        conflict=conflict,
        chorus=chorus,
        foundation=foundation,
        interpretation=interp,
        person_name="Игорь",
    )
    # Runtime: deterministic scene bank retired — empty until native LLM attaches scenes.
    assert scenes == []

    scenario = build_day_scenario_v1(
        interpretation=interp,
        day_events_pack=pack,
        day_thesis=thesis,
        ritual_context=ritual,
        person_name="Игорь",
    )
    # Deterministic path: empty forces → short_name is not A|B bank paste
    forces = scenario["conflict"].get("opposing_forces") or {}
    assert not (forces.get("a") and forces.get("b"))
    short = str(scenario["conflict"].get("short_name") or "")
    assert "тащить старое" not in short.lower()
    assert "меркурий" not in short.lower()
    assert find_verbatim_seed_leaks_v1(scenario) == []
    # Empty scenes are structurally invalid for meaning SoT (B5 unavailable).
    assert "scenes_empty" in validate_day_scenario_v1(scenario)


def test_chorus_bridges_are_lived_not_generation_meta():
    """v3.1b: no meta rules / tempo tag-dumps in user-facing chorus bridges."""
    from todayflow_backend.services.day_scenario_v1 import (
        build_scenario_props_v1,
        chorus_seed_paste_needs_heal_v1,
    )

    pack = _pack_merc_moon()
    ritual = {
        "tarot_name_ru": "Отшельник",
        "tarot_main_id": 9,
        "numerology_value": 7,
        "numerology_personal_day": 7,
    }
    foundation = build_scenario_foundation_v1(
        day_events_pack=pack,
        ritual_context=ritual,
        interpretation=None,
    )
    conflict = build_scenario_conflict_v1(foundation=foundation, day_thesis=None, interpretation=None)
    chorus = build_interpretive_chorus_v1(
        foundation=foundation,
        conflict_label=str(conflict.get("short_name") or ""),
        interpretation=None,
    )
    blob = " ".join(
        [
            str((chorus.get("day_card") or {}).get("human_meaning") or ""),
            str((chorus.get("day_card") or {}).get("way_to_relate") or ""),
            str((chorus.get("day_card") or {}).get("archetype_role") or ""),
            str((chorus.get("day_number") or {}).get("link_to_conflict") or ""),
            str((chorus.get("day_number") or {}).get("human_meaning") or ""),
            " ".join(
                str(r.get("human_meaning") or "")
                for r in (chorus.get("astrology") or [])
                if isinstance(r, dict)
            ),
        ]
    ).lower()
    banned = (
        "параллельного сюжета",
        "не отдельный прогноз",
        "не второй сюжет",
        "темп —",
        "способ —",
        "связывает этот небесный фактор",
        "проживите день в ключе",
        "без параллельного",
    )
    for phrase in banned:
        assert phrase not in blob, phrase
    number_bridge = str((chorus.get("day_number") or {}).get("human_meaning") or "")
    assert "число 7" in number_bridge.lower()
    assert "темп —" not in number_bridge.lower()
    assert "просит:" in number_bridge.lower()
    assert not chorus_seed_paste_needs_heal_v1(
        chorus, short_name=str(conflict.get("short_name") or "")
    )

    scenes = [
        {
            "scene_id": "s1",
            "sphere": "work",
            "sphere_label_ru": "Работа и решения",
            "role_in_story": "primary",
            "trap": "спешка в ответе",
            "recommended_action": "Один ясный ответ до обеда.",
            "evidence_references": [],
            "chorus_references": [],
        }
    ]
    props = build_scenario_props_v1(conflict=conflict, scenes=scenes, chorus=chorus)
    color = props.get("color") or {}
    link = str(color.get("link_to_conflict") or "")
    effect = str(color.get("expected_effect_today") or "")
    assert link
    assert "помогает удержать" in effect.lower()
    assert link not in effect
    avoid = props.get("avoid_color") or {}
    why = str(avoid.get("why") or "")
    name = str(avoid.get("name") or "")
    if name and why:
        assert not why.lower().startswith(name.lower())


def test_color_catalog_is_knowledge_not_sot():
    from todayflow_backend.services.day_color_catalog_v1 import (
        LAYER_B_PRIMARY_TAGS,
        PENDING_LAYER_B_COLORS,
        list_color_knowledge,
        validate_color_catalog_v1,
    )
    from todayflow_backend.services.day_scenario_v1 import _needed_color_tags

    rows = list_color_knowledge()
    assert len(rows) == 20  # 8 core + 6 layer-A + 6 layer-B
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
        "Шампань",
    } <= names
    assert PENDING_LAYER_B_COLORS == frozenset()

    # Sphere/keyword Layer-B tags reachable from _needed_color_tags
    probes = [
        _needed_color_tags(trap="", force_a="", sphere="creativity", mode=""),
        _needed_color_tags(trap="", force_a="", sphere="home", mode=""),
        _needed_color_tags(trap="", force_a="", sphere="money", mode=""),
        _needed_color_tags(trap="страсть и желание", force_a="", sphere="relationships", mode=""),
        _needed_color_tags(trap="отпустить тему и завершить", force_a="", sphere="home", mode=""),
    ]
    reachable = set().union(*probes)
    sphere_kw_tags = LAYER_B_PRIMARY_TAGS - {"quiet_celebration", "light_gratitude"}
    assert sphere_kw_tags <= reachable
    # Celebration tags are live in the catalog bank (unlocked via day_favorable)
    assert {"quiet_celebration", "light_gratitude"} <= LAYER_B_PRIMARY_TAGS

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
    from todayflow_backend.services.day_scenario_v1 import (
        _needed_color_tags,
        build_scenario_props_v1,
    )

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

    # day_favorable unlocks Champagne when no competing specialty trap
    props = build_scenario_props_v1(
        conflict={
            "short_name": "лёгкий день",
            "opposing_forces": {"a": "автопилот", "b": "выбор"},
            "thesis": {"mode": "stability"},
        },
        scenes=[
            {
                "scene_id": "s1",
                "role_in_story": "primary",
                "sphere": "relationships",
                "sphere_label_ru": "Отношения",
                "trap": "мягкий фон без острого конфликта",
            }
        ],
        day_favorable=True,
    )
    assert props.get("color", {}).get("name") == "Шампань"


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
