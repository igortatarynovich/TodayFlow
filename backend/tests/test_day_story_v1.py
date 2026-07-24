"""Tests for day_story_v1 — single canonical Today narrative artifact + PR-3 trace."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from todayflow_backend.services.day_story_interpretation_v1 import (
    build_day_story_interpretation_v1,
)
from todayflow_backend.services.day_story_phrase_gate_v1 import (
    day_story_passes_phrase_gate,
    find_empty_formula_hits,
)
from todayflow_backend.services.day_story_v1 import (
    DAY_STORY_V1_CONTRACT,
    build_day_story_fallback_v1,
    day_story_to_legacy_narrative,
    day_story_to_today_contract_v1,
    validate_day_story_v1,
)


def _sample_story() -> dict:
    story = build_day_story_fallback_v1(
        day_engine_brief={
            "anchor_summary": "Сегодня — один ясный шаг вместо распыления.",
            "do_hint": "Выбери одну задачу и доведи до видимого результата",
            "avoid_hint": "Не подписывайся на новые обязательства из импульса",
            "tempo_hint": "Держи ровный темп.",
            "thread_head_topic": "career",
        },
        color="лазурь",
        stone="сапфир",
        ritual_context={"head_topic": "career", "mood": "calm"},
        intent_slice={"what_matters_line": "закрыть один рабочий приоритет"},
        fingerprint="fp-test",
    )
    return story


def test_interpretation_always_builds_foundation_without_sky():
    from datetime import date

    interp = build_day_story_interpretation_v1(
        day_engine_brief={"anchor_summary": "Ось дня.", "do_hint": "Шаг.", "avoid_hint": "Не спеши."},
        ritual_context={},
        target_date=date(2026, 7, 24),
        birth_date=date(1990, 3, 15),
    )
    assert interp["source_inputs"]["has_day_foundation"] is True
    assert interp["source_inputs"]["target_date"] == "2026-07-24"
    assert interp["source_inputs"]["has_birth_date"] is True
    foundation = interp["day_foundation"]
    assert foundation["numerology"]["universal_day"] == 5
    assert foundation["numerology"]["personal_day"] is not None
    assert foundation["weekday"]["ruler_planet"] == "Venus"
    claim_ids = {c["id"] for c in interp["derived_claims"]}
    assert "claim.foundation.numerology" in claim_ids
    assert "claim.foundation.weekday" in claim_ids


def test_interpretation_includes_sky_and_color_why_claims():
    interp = build_day_story_interpretation_v1(
        day_engine_brief={"anchor_summary": "Ось дня.", "do_hint": "Шаг.", "avoid_hint": "Не спеши."},
        ritual_context={},
        celestial_events={
            "lunar_phase": {"name": "Убывающая луна", "guidance": "Отпускай лишнее."},
            "ingresses": [
                {
                    "planet": "mercury",
                    "planet_ru": "Меркурий",
                    "sign_ru": "Рак",
                    "story_ru": "Меркурий переходит в Рак — меняется тон разговоров.",
                }
            ],
            "sky_aspects": [
                {
                    "id": "sun-square-moon",
                    "title": "Солнце — квадрат — Луна",
                    "story_ru": "Намерение и настроение расходятся.",
                }
            ],
        },
        color_symbol={
            "name": "Лазурь",
            "benefit_ru": "Держит ясность в коротких решениях.",
            "avoid_color_ru": "Кислотно-оранжевый",
            "avoid_why_ru": "Разгоняет темп.",
        },
        stone_symbol={"name": "лазурит", "story_ru": "Мягкая опора для спокойного тона."},
        color="Лазурь",
        stone="лазурит",
    )
    claim_ids = {c["id"] for c in interp["derived_claims"]}
    # With celestial present, foundation owns sky claims (not legacy claim.sky.*).
    assert "claim.day_axis" in claim_ids
    assert any(i.startswith("claim.foundation.astro.") for i in claim_ids)
    assert any(i.startswith("claim.foundation.lunar.") for i in claim_ids)
    assert "claim.talisman.color_why" in claim_ids
    assert "claim.talisman.stone_why" in claim_ids
    assert interp["day_sky"].get("moon")
    assert interp.get("day_foundation", {}).get("essence", {}).get("story_ru")
    assert interp["calculation_version"].startswith("day-story-interpretation-v1.2")


def test_fallback_fills_talisman_note_from_color_why():
    story = build_day_story_fallback_v1(
        day_engine_brief={
            "anchor_summary": "Сегодня — один ясный шаг вместо распыления.",
            "do_hint": "Выбери одну задачу и доведи до видимого результата",
            "avoid_hint": "Не подписывайся на новые обязательства из импульса",
            "tempo_hint": "Держи ровный темп.",
            "thread_head_topic": "career",
        },
        color="Лазурь",
        stone="лазурит",
        color_symbol={
            "name": "Лазурь",
            "benefit_ru": "Держит ясность в коротких решениях.",
        },
        ritual_context={"head_topic": "career", "mood": "calm"},
        intent_slice={"what_matters_line": "закрыть один рабочий приоритет"},
        fingerprint="fp-test",
    )
    assert "ясность" in (story.get("talisman") or {}).get("note", "").lower()
    assert story.get("supports_story")
    contract = day_story_to_today_contract_v1(story, generation_id="1")
    assert contract["day_story"].get("supports_story")


def test_interpretation_no_domains_without_topic():
    interp = build_day_story_interpretation_v1(
        day_engine_brief={"anchor_summary": "Ось дня.", "do_hint": "Шаг.", "avoid_hint": "Не спеши."},
        ritual_context={},
    )
    assert interp["domains_present"] == []
    assert set(interp["domains_absent"]) == {"relationships", "money_work", "family"}


def test_validate_day_story_v1_green_on_fallback():
    assert validate_day_story_v1(_sample_story()) == []


def test_build_day_story_fallback_has_trace_and_partial_domains():
    story = _sample_story()
    assert story["contract_version"] == DAY_STORY_V1_CONTRACT
    assert "trace" in story
    assert story["trace"]["evidence"]
    assert story["trace"]["derived_claims"]
    assert story["trace"]["calculation_version"]
    assert "money_work" in story["domains"]
    assert "family" not in story["domains"] or story["domains"].get("family", {}).get("evidence_status") != "present"


def test_day_story_to_today_contract_marks_absent_domains():
    contract = day_story_to_today_contract_v1(_sample_story(), generation_id="42", progress={})
    assert contract["contract_version"] == "today_contract_v1"
    assert contract["generation_id"] == "42"
    assert contract["domains"]["money_work"].get("evidence_status") == "present"
    assert contract["domains"]["family"].get("evidence_status") == "absent"
    assert contract["domains"]["family"]["status"] == ""
    assert contract["day_story"]["trace"]["confidence"] is not None
    assert "story_limitations" in contract["progress"]


def test_day_story_to_today_contract_forwards_day_personal():
    story = _sample_story()
    story["day_personal"] = {
        "contract_version": "day_personal_v1",
        "summary_ru": "Firdaria и управители.",
        "personal_astrology": {
            "capability_ids": ["house_rulers_chains", "time_lords"],
            "house_rulers_chains": {"summary_ru": "Управители домов soft."},
            "time_lords": {"summary_ru": "Firdaria: мажор Луна."},
        },
        "human_design": {
            "channels": {"summary_ru": "Каналы HD soft."},
        },
    }
    contract = day_story_to_today_contract_v1(story, generation_id="dp-1")
    personal = contract["day_story"].get("day_personal")
    assert isinstance(personal, dict)
    assert personal["personal_astrology"]["time_lords"]["summary_ru"]
    assert personal["human_design"]["channels"]["summary_ru"]


def test_day_story_to_legacy_narrative_derives_surfaces():
    story = _sample_story()
    narrative = day_story_to_legacy_narrative(story, generation_id="42")
    assert narrative["guide"]["payload"]["headline"] == story["theme"]
    assert narrative["spheres"]["payload"]["page_intro"] == story["story"]
    assert narrative["day_layer"]["payload"]["nudge_message"] == story["today_move"]
    assert narrative["evening"]["payload"]["panel_intro"]


def test_phrase_gate_rejects_empty_formulas():
    bad = _sample_story()
    bad["story"] = "Сегодня лучше довериться потоку и выбрать главное."
    ok, hits = day_story_passes_phrase_gate(bad)
    assert not ok
    assert hits
    assert find_empty_formula_hits(bad)


def test_validate_rejects_empty_formula_story():
    bad = _sample_story()
    bad["theme"] = "Довериться потоку"
    errors = validate_day_story_v1(bad)
    assert any("empty_formula" in e for e in errors)
