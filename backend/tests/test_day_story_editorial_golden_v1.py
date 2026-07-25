"""Formula bank is QA/golden only — runtime fallback must not ship formula prose."""

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
    INTERPRETATION_UNAVAILABLE_RU,
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
def test_runtime_fallback_is_facts_only_not_formula(case: dict):
    formula = lookup_editorial_formula(family=case["family"], variant=case["variant"])
    assert formula is not None

    story = build_day_story_fallback_v1(
        day_engine_brief={"anchor_summary": "тест", "do_hint": "", "avoid_hint": ""},
        interpretation=_interp_for_case(case),
        locale="ru",
    )

    errors = validate_day_story_v1(story)
    assert not errors, errors
    assert story.get("interpretation_status") == "unavailable"
    assert INTERPRETATION_UNAVAILABLE_RU in str(story.get("interpretation_unavailable_message") or "")

    # No formula prose in user slots
    assert not str(story.get("expect") or "").strip()
    assert not str(story.get("trap") or "").strip()
    assert not (story.get("do") or [])
    assert not (story.get("avoid") or [])
    assert not str(story.get("vibe_closing") or "").strip()
    assert formula["expect"] not in str(story.get("story") or "")

    thesis = story.get("day_thesis") or {}
    assert thesis.get("family") == case["family"]
    assert thesis.get("variant") == case["variant"]

    lead = str(story.get("events_lead") or "").lower()
    assert any(str(d.get("fact_ru") or "").lower()[:20] in lead for d in case["drivers"])

    contract = day_story_to_today_contract_v1(story, generation_id="golden-1")
    ds = contract.get("day_story") or {}
    assert ds.get("interpretation_status") == "unavailable"
    assert not str(ds.get("expect") or "").strip()
    # Domain fallback templates must not appear
    for did, lens in (contract.get("domains") or {}).items():
        assert str(lens.get("evidence_status") or "") == "absent"
        assert not str(lens.get("action") or "").strip()


def test_editorial_formula_bank_covers_exemplars():
    keys = set(list_editorial_formula_keys())
    assert "communication.clarity_returns_after_delay" in keys
    assert "change.sudden_turns" in keys
    assert "decision.stop_pleasing_everyone" in keys


def test_editorial_formula_bank_covers_all_thesis_variants():
    from todayflow_backend.services.day_thesis_v1 import list_day_thesis_variant_keys

    thesis_keys = set(list_day_thesis_variant_keys())
    formula_keys = set(list_editorial_formula_keys())
    missing = sorted(thesis_keys - formula_keys)
    assert not missing, f"editorial formulas missing for: {missing}"


@pytest.mark.parametrize("key", list_editorial_formula_keys())
def test_every_formula_row_is_phrase_clean_for_qa(key: str):
    """QA corpus hygiene — formulas themselves must not contain empty chrome."""
    family, variant = key.split(".", 1)
    formula = lookup_editorial_formula(family=family, variant=variant)
    assert formula is not None
    story = {
        "expect": formula["expect"],
        "trap": formula["trap"],
        "do": formula["do"],
        "avoid": formula["avoid"],
        "vibe_closing": formula["vibe_closing"],
        "theme": formula.get("theme") or "",
        "headline_anchor": formula.get("headline_anchor") or "",
        "primary_conflict": formula.get("headline_anchor") or "",
        "day_thesis": {"label_ru": formula.get("headline_anchor") or "", "family": family, "variant": variant},
        "story": formula["expect"],
        "direction": formula["expect"],
        "advantage": formula["do"][0],
        "abstain": formula["trap"],
        "today_move": formula["do"][0],
        "global_period": formula.get("theme") or "",
        "development_point": formula.get("development_point") or "x",
        "domains": {},
    }
    ok, hits = day_story_passes_phrase_gate(story)
    assert ok, hits
    strokes = formula.get("vibe_strokes") or []
    # strokes optional on older rows
    assert str(formula.get("expect") or "").strip()
    assert str(formula.get("trap") or "").strip()
    _ = strokes


def test_every_formula_links_valid_strong_patterns():
    from todayflow_backend.services.day_story_editorial_formulas_v1 import list_strong_pattern_links

    links = list_strong_pattern_links()
    for key in list_editorial_formula_keys():
        assert key in links, f"missing SP link for {key}"
        ids = links[key]
        assert ids and all(str(x).startswith("SP-") for x in ids)
