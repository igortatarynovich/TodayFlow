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


def test_interpretation_marks_domain_from_head_topic():
    interp = build_day_story_interpretation_v1(
        day_engine_brief={"anchor_summary": "Ось дня.", "do_hint": "Шаг.", "avoid_hint": "Не спеши."},
        ritual_context={"head_topic": "love"},
    )
    assert "relationships" in interp["domains_present"]
    assert "family" in interp["domains_absent"]
    assert interp["evidence"]
    assert interp["derived_claims"]
    assert interp["confidence"] is not None
    assert interp["limitations"]


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
