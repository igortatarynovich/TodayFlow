"""Golden fixtures: editorial formula A–C → day_story fallback (RULE_005).

Not TL-1 language quality — checks one thesis + expect/trap/do/avoid/vibe fill.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from todayflow_backend.services.day_story_editorial_formulas_v1 import (
    list_editorial_formula_keys,
    lookup_editorial_formula,
)
from todayflow_backend.services.day_story_phrase_gate_v1 import day_story_passes_phrase_gate
from todayflow_backend.services.day_story_v1 import (
    build_day_story_fallback_v1,
    day_story_to_today_contract_v1,
    validate_day_story_v1,
)

_FIXTURE = Path(__file__).parent / "fixtures" / "day_story_editorial" / "golden_v1.json"


def _load_cases() -> list[dict]:
    raw = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    return list(raw.get("cases") or [])


def _interp_for_case(case: dict) -> dict:
    drivers = case.get("drivers") or []
    events = []
    for d in drivers:
        events.append(
            {
                "id": d["id"],
                "kind": d.get("kind"),
                "title_ru": d.get("title_ru"),
                "fact_ru": d.get("fact_ru"),
                "priority_hint": "primary",
                "strength": 0.9,
            }
        )
    driver_ids = [str(d["id"]) for d in drivers]
    pack = {
        "contract_version": "day_events_pack_v1",
        "ranked_drivers": driver_ids,
        "events": events,
        "ambient": [],
        "compositions": [],
        "role": "evidence",
    }
    thesis = {
        "contract_version": "day_thesis_v1",
        "family": case["family"],
        "variant": case["variant"],
        "mode": case["mode"],
        "label_ru": case["label_ru"],
        "driver_ids": driver_ids,
        "composition_ids": [],
    }
    return {
        "contract_version": "day_story_interpretation_v1",
        "calculation_version": "day-story-interpretation-v1.3",
        "confidence": 0.72,
        "limitations": [],
        "evidence": [],
        "derived_claims": [],
        "domains_present": [],
        "domains_absent": [],
        "fingerprint": f"golden-{case['id']}",
        "day_thesis": thesis,
        "primary_conflict": {
            "label_ru": case["label_ru"],
            "driver_ids": driver_ids,
            "day_thesis": thesis,
        },
        "day_events_pack": pack,
        "day_foundation": {"essence": {"theme": "", "story_ru": ""}},
    }


@pytest.mark.parametrize("case", _load_cases(), ids=lambda c: c["id"])
def test_editorial_golden_fallback_fills_formula(case: dict):
    formula = lookup_editorial_formula(family=case["family"], variant=case["variant"])
    assert formula is not None, f"missing formula for {case['family']}.{case['variant']}"

    story = build_day_story_fallback_v1(
        day_engine_brief={"anchor_summary": "тест", "do_hint": "", "avoid_hint": ""},
        interpretation=_interp_for_case(case),
        locale="ru",
    )

    errors = validate_day_story_v1(story)
    assert not errors, errors
    ok, hits = day_story_passes_phrase_gate(story)
    assert ok, hits

    thesis = story.get("day_thesis") or {}
    assert thesis.get("family") == case["family"]
    assert thesis.get("variant") == case["variant"]
    assert story.get("primary_conflict") == thesis.get("label_ru")

    blob_expect = str(story.get("expect") or "").lower()
    for token in case.get("expect_contains") or []:
        assert token.lower() in blob_expect, f"expect missing {token!r}: {story.get('expect')}"

    blob_trap = str(story.get("trap") or "").lower()
    for token in case.get("trap_contains") or []:
        assert token.lower() in blob_trap, f"trap missing {token!r}: {story.get('trap')}"

    do_blob = " ".join(str(x) for x in (story.get("do") or [])).lower()
    assert any(t.lower() in do_blob for t in (case.get("do_contains_any") or [])), story.get("do")

    avoid_blob = " ".join(str(x) for x in (story.get("avoid") or [])).lower()
    assert any(t.lower() in avoid_blob for t in (case.get("avoid_contains_any") or [])), story.get(
        "avoid"
    )

    vibe = str(story.get("vibe_closing") or "").lower()
    assert any(t.lower() in vibe for t in (case.get("vibe_contains_any") or [])), story.get(
        "vibe_closing"
    )

    theme = str(story.get("theme") or story.get("headline_anchor") or "").lower()
    assert case["theme_contains"].lower() in theme

    # events_lead must mention drivers, not invent a second plot
    lead = str(story.get("events_lead") or "").lower()
    assert any(str(d.get("fact_ru") or "").lower()[:20] in lead for d in case["drivers"])

    contract = day_story_to_today_contract_v1(story, generation_id="golden-1")
    ds = contract.get("day_story") or {}
    assert (ds.get("day_thesis") or {}).get("variant") == case["variant"]
    assert ds.get("primary_conflict") == (ds.get("day_thesis") or {}).get("label_ru")


def test_editorial_formula_bank_covers_exemplars():
    keys = set(list_editorial_formula_keys())
    assert "communication.clarity_returns_after_delay" in keys
    assert "change.sudden_turns" in keys
    assert "decision.stop_pleasing_everyone" in keys
