"""1.3.118 Native C1 evidence pack binding — unknown_evidence aliases, not gate weakening."""

from __future__ import annotations

from pathlib import Path

from todayflow_backend.services.day_scenario_native_llm_c1 import (
    brief_cite_list,
    collect_allowed_evidence_ids,
    collect_foundation_cite_ids,
    format_unknown_evidence_retry_feedback,
    foundation_cite_aliases,
    normalize_native_scenario_llm_c1,
    validate_native_scenario_llm_c1,
)
from tests.test_day_scenario_native_llm_c1 import _valid_native

ROOT = Path(__file__).resolve().parents[2]
BINDING_CANON = ROOT / "docs" / "today" / "NATIVE_C1_EVIDENCE_PACK_BINDING_V1.md"

GEN1092_ASPECT = "ev.foundation.lunar.aspect.sky-moon-opposition-mars"
GEN1092_INGRESS = "ev.foundation.lunar.ingress.Moon"


def _thin_foundation() -> dict:
    return {
        "lunar": {
            "beats": [
                {
                    "id": "aspect.sky-moon-opposition-mars",
                    "kind": "aspect",
                    "title": "Луна оппозиция Марс",
                    "evidence_ref": "source.moon.aspects",
                },
                {
                    "id": "ingress.Moon",
                    "kind": "ingress",
                    "title": "Луна → знак",
                    "evidence_ref": "source.moon.ingresses",
                },
            ]
        },
        "astro": {"beats": []},
        "essence": {"evidence_ids": ["lunar.summary"]},
    }


def test_binding_canon_exists():
    assert BINDING_CANON.is_file()
    text = BINDING_CANON.read_text(encoding="utf-8")
    assert "unknown_evidence" in text
    assert "gen 1092" in text or "1092" in text


def test_foundation_aliases_cover_gen1092_path_cites():
    aliases = foundation_cite_aliases(
        layer="lunar",
        beat_id="aspect.sky-moon-opposition-mars",
        evidence_ref="source.moon.aspects",
    )
    assert GEN1092_ASPECT in aliases
    assert "aspect.sky-moon-opposition-mars" in aliases
    assert "claim.foundation.lunar.aspect.sky-moon-opposition-mars" in aliases
    assert "ev.claim.foundation.lunar.aspect.sky-moon-opposition-mars" in aliases
    retro = foundation_cite_aliases(layer="astro", beat_id="retro.Saturn")
    assert "ev.foundation.astro.retro.Saturn" in retro


def test_thin_profile_foundation_ids_are_allowed():
    allowed = collect_allowed_evidence_ids(
        interpretation={},
        day_foundation=_thin_foundation(),
    )
    assert GEN1092_ASPECT in allowed
    assert GEN1092_INGRESS in allowed
    native = _valid_native()
    native["conflict"]["driver_refs"] = [GEN1092_INGRESS]
    native["conflict"]["evidence_refs"] = [GEN1092_ASPECT]
    native["interpretive_chorus"]["astrology"][0]["evidence_refs"] = [GEN1092_ASPECT]
    native["scenes"][0]["evidence_refs"] = [GEN1092_ASPECT]
    native["scenes"][1]["evidence_refs"] = [GEN1092_INGRESS]
    errors = validate_native_scenario_llm_c1(
        normalize_native_scenario_llm_c1(native),
        allowed_evidence_ids=allowed,
    )
    assert not any(str(e).startswith("unknown_evidence:") for e in errors)


def test_invented_evidence_still_rejected():
    allowed = collect_allowed_evidence_ids(
        interpretation={},
        day_foundation=_thin_foundation(),
    )
    native = _valid_native()
    native["conflict"]["driver_refs"] = ["invented-planet-42"]
    errors = validate_native_scenario_llm_c1(
        normalize_native_scenario_llm_c1(native),
        allowed_evidence_ids=allowed,
    )
    assert any("unknown_evidence" in e for e in errors)


def test_ranked_drivers_strings_are_allowed():
    allowed = collect_allowed_evidence_ids(
        interpretation={
            "day_events_pack": {
                "ranked_drivers": ["moon-pisces", "merc-direct"],
                "ambient": ["venus-aspect"],
                "events": [],
            }
        }
    )
    assert "moon-pisces" in allowed
    assert "merc-direct" in allowed
    assert "venus-aspect" in allowed
    assert "ev.driver.moon-pisces" in allowed


def test_brief_cite_list_omits_path_aliases():
    allowed = collect_foundation_cite_ids(_thin_foundation())
    allowed.update({"moon-pisces", "day_card"})
    listed = brief_cite_list(allowed, prefer=["moon-pisces"])
    assert listed[0] == "moon-pisces"
    assert GEN1092_ASPECT not in listed
    assert "day_card" in listed


def test_unknown_evidence_retry_names_allowed_ids():
    fb = format_unknown_evidence_retry_feedback(
        [f"unknown_evidence:conflict:{GEN1092_ASPECT}"],
        allowed_evidence_ids={"moon-pisces", "day_card"},
    )
    assert "unknown_evidence" in fb
    assert "moon-pisces" in fb
    assert "allowed_evidence_ids" in fb
